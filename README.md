# 📊 Dashboard des ventes e-commerce

Tableau de bord interactif développé avec **Streamlit** et **Plotly**, branché sur l'entrepôt de données (schéma en étoile) produit par mon projet [Pipeline ETL – Ventes e-commerce](https://github.com/VOTRE-PSEUDO/etl-ventes-ecommerce).

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat&logo=sqlite&logoColor=white)

<!-- Ajoutez ici une capture d'écran : docs/apercu.png -->
<!-- ![Aperçu du dashboard](docs/apercu.png) -->

---

## Fonctionnalités

- **Filtres** : période, catégories de produits, villes
- **KPI** : chiffre d'affaires, nombre de commandes, panier moyen, taux d'annulation
- **Graphiques** : évolution mensuelle du CA, CA par catégorie, commandes par jour de la semaine, panier moyen par ville
- **Top 10 des produits** par chiffre d'affaires
- **Export CSV** des données filtrées

## Ce que montrent les données

- Un pic de ventes net en **novembre-décembre** (saisonnalité des fêtes)
- Les **tablettes et écrans** concentrent la plus grande part du chiffre d'affaires
- Un taux d'annulation élevé (~23 %), point d'attention pour l'équipe commerciale

---

## Lancer le projet

```bash
pip install -r requirements.txt
streamlit run app.py
```

Puis ouvrir http://localhost:8501.

Avec Docker :

```bash
docker build -t dashboard-ventes .
docker run -p 8501:8501 dashboard-ventes
```

## Données

`data/entrepot.db` est une base SQLite générée par le pipeline ETL. Le dashboard lit la table de faits `fait_ventes` jointe aux dimensions `dim_date`, `dim_produit` et `dim_client` en une seule requête SQL, mise en cache avec `st.cache_data`.

## Déploiement gratuit

Le dashboard peut être mis en ligne gratuitement sur [Streamlit Community Cloud](https://streamlit.io/cloud) : connectez votre compte GitHub, choisissez ce dépôt et le fichier `app.py`. Vous obtenez un lien public à mettre sur votre CV.

---

👩‍💻 Réalisé par **Ikram Guesmi** — [LinkedIn](https://www.linkedin.com/in/ikram-guesmi75)
