"""
Dashboard des ventes e-commerce.
Lancement : streamlit run app.py
"""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).parent / "data" / "entrepot.db"
COULEUR = "#2563eb"
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

st.set_page_config(page_title="Dashboard ventes", page_icon="📊", layout="wide")


@st.cache_data
def charger_donnees() -> pd.DataFrame:
    """Une seule requête : la table de faits jointe à ses dimensions."""
    requete = """
        SELECT f.id_commande, f.quantite, f.montant, f.statut,
               d.date, d.annee, d.mois, d.jour_semaine,
               p.nom AS produit, p.categorie,
               c.ville, c.id_client
        FROM fait_ventes f
        JOIN dim_date d    ON d.id_date = f.id_date
        JOIN dim_produit p ON p.id_produit = f.id_produit
        JOIN dim_client c  ON c.id_client = f.id_client
    """
    with sqlite3.connect(BASE) as connexion:
        df = pd.read_sql(requete, connexion)
    df["date"] = pd.to_datetime(df["date"])
    df["mois_annee"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


def euros(valeur: float) -> str:
    return f"{valeur:,.0f} €".replace(",", " ")


df = charger_donnees()

# ---------- Filtres ----------
st.sidebar.header("Filtres")
date_min, date_max = df["date"].min().date(), df["date"].max().date()
periode = st.sidebar.date_input("Période", (date_min, date_max), min_value=date_min, max_value=date_max)
categories = st.sidebar.multiselect("Catégories", sorted(df["categorie"].unique()))
villes = st.sidebar.multiselect("Villes", sorted(df["ville"].unique()))

filtre = df
if isinstance(periode, tuple) and len(periode) == 2:
    filtre = filtre[(filtre["date"].dt.date >= periode[0]) & (filtre["date"].dt.date <= periode[1])]
if categories:
    filtre = filtre[filtre["categorie"].isin(categories)]
if villes:
    filtre = filtre[filtre["ville"].isin(villes)]

st.title("📊 Dashboard des ventes")
st.caption("Données issues de l'entrepôt construit par le pipeline ETL (schéma en étoile).")

if filtre.empty:
    st.warning("Aucune vente pour ces filtres.")
    st.stop()

# ---------- KPI ----------
valides = filtre[filtre["statut"] != "annulée"]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Chiffre d'affaires", euros(filtre["montant"].sum()))
k2.metric("Commandes", f"{len(filtre):,}".replace(",", " "))
k3.metric("Panier moyen", euros(valides["montant"].mean()) if len(valides) else "—")
k4.metric("Taux d'annulation", f"{(filtre['statut'] == 'annulée').mean():.1%}".replace(".", ","))

# ---------- Graphiques ----------
gauche, droite = st.columns([3, 2])

with gauche:
    st.subheader("Évolution du chiffre d'affaires")
    mensuel = filtre.groupby("mois_annee", as_index=False)["montant"].sum()
    fig = px.line(mensuel, x="mois_annee", y="montant", markers=True,
                  labels={"mois_annee": "", "montant": "CA (€)"})
    fig.update_traces(line_color=COULEUR)
    st.plotly_chart(fig, width="stretch")

with droite:
    st.subheader("CA par catégorie")
    par_cat = filtre.groupby("categorie", as_index=False)["montant"].sum().sort_values("montant")
    fig = px.bar(par_cat, x="montant", y="categorie", orientation="h",
                 labels={"montant": "CA (€)", "categorie": ""})
    fig.update_traces(marker_color=COULEUR)
    st.plotly_chart(fig, width="stretch")

gauche, droite = st.columns(2)

with gauche:
    st.subheader("Commandes par jour de la semaine")
    par_jour = (filtre.groupby("jour_semaine").size()
                .reindex(JOURS, fill_value=0).rename("commandes").reset_index())
    fig = px.bar(par_jour, x="jour_semaine", y="commandes", labels={"jour_semaine": ""})
    fig.update_traces(marker_color=COULEUR)
    st.plotly_chart(fig, width="stretch")

with droite:
    st.subheader("Top 10 des produits")
    top = (filtre.groupby(["produit", "categorie"], as_index=False)
           .agg(quantite=("quantite", "sum"), chiffre_affaires=("montant", "sum"))
           .sort_values("chiffre_affaires", ascending=False).head(10))
    st.dataframe(top, hide_index=True, width="stretch",
                 column_config={"chiffre_affaires": st.column_config.NumberColumn("CA (€)", format="%.0f €")})

st.subheader("Panier moyen par ville")
par_ville = (valides.groupby("ville", as_index=False)
             .agg(panier_moyen=("montant", "mean"), commandes=("id_commande", "count"))
             .sort_values("panier_moyen", ascending=False))
fig = px.bar(par_ville, x="ville", y="panier_moyen", hover_data=["commandes"],
             labels={"ville": "", "panier_moyen": "Panier moyen (€)"})
fig.update_traces(marker_color=COULEUR)
st.plotly_chart(fig, width="stretch")

with st.expander("Voir les données filtrées"):
    st.dataframe(filtre.drop(columns=["mois_annee"]), hide_index=True, width="stretch")
    st.download_button("Télécharger en CSV", filtre.to_csv(index=False).encode("utf-8"),
                       "ventes_filtrees.csv", "text/csv")
