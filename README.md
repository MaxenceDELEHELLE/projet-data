# Accidents Vélo en France — Dashboard interactif

Projet réalisé dans le cadre de l'unité **Python Avancé**
Professeur : **Daniel COURIVAUD**
Étudiants : **Maxence DELEHELLE** — **Amine SAAD-EDDINE**

---

## Lien Vidéo présentation

https://youtu.be/AKtw75KEcX8

## Description

Ce projet analyse la relation entre les **infrastructures cyclables** et les **accidents de vélo** dans les 60 plus grandes villes de France.

Il s'appuie sur des données publiques issues de plusieurs APIs open data, les nettoie et les enrichit, puis les expose dans un **dashboard interactif Dash/Plotly** permettant de visualiser :

- les KPIs globaux (nb villes, km de pistes, accidents totaux, proportion moyenne)
- le classement des villes par proportion de voies cyclables
- une carte à bulles géolocalisée (taille = accidents, couleur = proportion cyclable)
- la corrélation entre proportion de voies cyclables et taux d'accidents vélo
- l'évolution temporelle des accidents par catégorie d'infrastructure
- un tableau de données filtrable par ville

---

## Structure du projet

```
projet_data/
│
├── data/
│   ├── raw/                              # Données brutes téléchargées
│   │   ├── accidentsVelo.db              # Accidents vélo historiques (SQLite)
│   │   ├── accidents_2023.csv            # Caractéristiques accidents 2023
│   │   ├── amenagements_cyclables.geojson  # Aménagements cyclables France (Parquet → CSV)
│   │   └── communes_idf.geojson          # Top 60 communes par population (GeoJSON)
│   └── cleaned/                          # Données nettoyées (cache)
│       ├── villes_clean.csv              # Indicateurs par ville
│       └── timeseries_clean.csv          # Série temporelle accidents par ville/année
│
├── src/
│   ├── utils/
│   │   ├── get_data.py                   # Récupération des données via APIs
│   │   └── clean_data.py                 # Nettoyage, fusion et calcul des indicateurs
│   ├── components/
│   │   ├── header.py                     # En-tête du dashboard
│   │   ├── footer.py                     # Pied de page
│   │   ├── kpi_cards.py                  # 4 cartes de KPI (résumé global)
│   │   ├── histogram.py                  # Barres horizontales : classement des villes
│   │   ├── map_chart.py                  # Carte à bulles géolocalisée (Scattergeo)
│   │   ├── scatter.py                    # Nuage de points avec régression linéaire
│   │   └── timeseries.py                 # Série temporelle par catégorie
│   └── pages/
│       └── home.py                       # Assemblage du layout principal
│
├── assets/
│   └── style.css                         # Styles CSS personnalisés
│
├── main.py                               # Point d'entrée : pipeline données + app Dash
├── config.py                             # Configuration centralisée (chemins, serveur)
├── generate_sample_data.py               # Génération de données d'exemple (fallback)
├── requirements.txt
└── README.md
```

---

## Sources de données

| Source | Contenu | Format |
|--------|---------|--------|
| [OpenData Koumoul](https://opendata.koumoul.com) | Accidents vélo France (historique) | CSV → SQLite |
| [data.gouv.fr](https://static.data.gouv.fr) | Caractéristiques accidents 2023 | CSV |
| [transport.data.gouv.fr](https://transport.data.gouv.fr/datasets/amenagements-cyclables-france-metropolitaine) | Aménagements cyclables France (Geovelo) | Parquet → CSV |
| [geo.api.gouv.fr](https://geo.api.gouv.fr) | Communes françaises avec population | GeoJSON |

---

## Installation

Prérequis : Python 3.10+

```bash
# Cloner le dépôt
git clone https://github.com/MaxenceDELEHELLE/projet-data
cd projet_data

# Créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

---

## Lancement

```bash
python3 main.py
```

Au premier lancement, le script :
1. Tente de télécharger les données depuis les 4 APIs
2. Nettoie et enrichit les données, puis les met en cache dans `data/cleaned/`
3. Lance le dashboard sur http://127.0.0.1:8050

Aux lancements suivants, les données sont chargées depuis le cache.
En cas d'échec des APIs, le script bascule automatiquement sur des données d'exemple générées par `generate_sample_data.py`.

---

## Dashboard

Le dashboard expose cinq visualisations interactives :

**KPI cards**
Résumé global : nombre de villes analysées, total km de pistes cyclables, total accidents vélo, proportion cyclable moyenne.

**Classement des villes (barres horizontales)**
Classement des N plus grandes villes par proportion de voies cyclables (km pistes / population × 10 000), avec curseur pour ajuster N.

**Carte à bulles (Scattergeo)**
Carte centrée sur la France : taille des bulles proportionnelle au nombre d'accidents, couleur encodant la proportion cyclable.

**Nuage de points avec régression**
Corrélation entre proportion de voies cyclables et taux d'accidents (pour 100 000 hab.), avec droite de régression et R². Filtrable par catégorie cyclable.

**Série temporelle**
Évolution du nombre d'accidents par année, regroupée par catégorie d'infrastructure cyclable (`< 2 %`, `2–5 %`, `5–8 %`, `> 8 %`).

**Tableau de données**
Tableau paginé de toutes les villes avec recherche par nom, tri par colonne.

---

## Pipeline de données

```
APIs publiques (Koumoul, data.gouv.fr, transport.data.gouv.fr, geo.api.gouv.fr)
    │
    ▼
get_data.py          ← téléchargement & stockage local (SQLite, CSV, GeoJSON)
    │
    ▼
clean_data.py        ← fusion des 3 sources, mapping arrondissements Paris/Lyon/Marseille,
    │                   calcul indicateurs (taux accidents, proportion cyclable, catégories)
    ▼
data/cleaned/        ← cache CSV (villes_clean.csv, timeseries_clean.csv)
    │
    ▼
main.py              ← création de l'app Dash, callbacks interactifs
    │
    ▼
Dashboard Dash       ← http://127.0.0.1:8050
```

---

## Dépendances

```
pandas==3.0.1
numpy==2.4.3
requests==2.33.0
plotly==6.7.0
dash==4.1.0
pyarrow==24.0.0
```
