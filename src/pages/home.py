"""
home.py
-------
Page principale du dashboard : assembles tous les composants visuels.
"""

from dash import html, dcc
import pandas as pd

from src.components.kpi_cards import build_kpi_cards
from src.components.histogram import build_histogram
from src.components.map_chart import build_map
from src.components.scatter import build_scatter
from src.components.timeseries import build_timeseries


def build_home_layout(df_villes: pd.DataFrame, df_ts: pd.DataFrame) -> html.Div:
    """
    Assemble la page principale du dashboard.

    Paramètres
    ----------
    df_villes : DataFrame nettoyé des villes
    df_ts     : DataFrame nettoyé de la série temporelle

    Retourne
    --------
    html.Div contenant l'ensemble de la page
    """
    return html.Div(
        className="page-content",
        children=[
            # ── KPI ─────────────────────────────────────────────────────────
            build_kpi_cards(df_villes),

            # ── Intro ────────────────────────────────────────────────────────
            html.Div(
                className="section-intro",
                children=[
                    html.H2("Les villes les plus cyclables ont-elles moins d'accidents ?"),
                    html.P(
                        "Cette étude croise les données d'aménagements cyclables "
                        "(proportion de voies dédiées aux vélos) avec les statistiques "
                        "d'accidentalité routière impliquant des cyclistes, "
                        "pour 60 grandes villes françaises."
                    ),
                ],
            ),

            # ── Section 1 : Histogramme ──────────────────────────────────────
            html.Div(
                className="card",
                children=[
                    html.H3("Classement des villes par infrastructure cyclable"),
                    html.P(
                        "Les barres montrent la proportion de voies cyclables "
                        "(% de la voirie totale). "
                        "En regard, le taux d'accidents vélo pour 100 000 habitants.",
                        className="chart-subtitle",
                    ),
                    html.Div(
                        className="histogram-controls",
                        children=[
                            html.Label("Nombre de villes affichées :"),
                            dcc.Slider(
                                id="slider-top-n",
                                min=10,
                                max=60,
                                step=5,
                                value=40,
                                marks={i: str(i) for i in range(10, 65, 10)},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="graph-histogram",
                        figure=build_histogram(df_villes, top_n=40),
                        config={"displayModeBar": False},
                    ),
                ],
            ),

            # ── Section 2 : Carte + Scatter ──────────────────────────────────
            html.Div(
                className="two-col",
                children=[
                    # Carte géolocalisée
                    html.Div(
                        className="card",
                        children=[
                            html.H3("Carte des villes"),
                            html.P(
                                "Taille des bulles = nombre d'accidents vélo · "
                                "Couleur = % voies cyclables",
                                className="chart-subtitle",
                            ),
                            dcc.Graph(
                                id="graph-map",
                                figure=build_map(df_villes),
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                    # Nuage de points
                    html.Div(
                        className="card",
                        children=[
                            html.H3("Corrélation infrastructure / accidentalité"),
                            html.P(
                                "Chaque point est une ville. La droite de régression "
                                "indique la tendance générale.",
                                className="chart-subtitle",
                            ),
                            html.Div(
                                className="scatter-controls",
                                children=[
                                    html.Label("Filtrer par catégorie :"),
                                    dcc.Checklist(
                                        id="checklist-categories",
                                        options=[
                                            {"label": " < 2 %", "value": "< 2 %"},
                                            {"label": " 2–5 %", "value": "2–5 %"},
                                            {"label": " 5–8 %", "value": "5–8 %"},
                                            {"label": " > 8 %", "value": "> 8 %"},
                                        ],
                                        value=["< 2 %", "2–5 %", "5–8 %", "> 8 %"],
                                        inline=True,
                                        className="category-checklist",
                                    ),
                                ],
                            ),
                            dcc.Graph(
                                id="graph-scatter",
                                figure=build_scatter(df_villes),
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                ],
            ),

            # ── Section 3 : Séries temporelles ──────────────────────────────
            html.Div(
                className="card",
                children=[
                    html.H3("Évolution de l'accidentalité vélo (2015–2023)"),
                    html.P(
                        "Nombre moyen d'accidents par ville, regroupé par niveau "
                        "d'infrastructure cyclable. Les villes mieux équipées "
                        "montrent une tendance à la baisse plus marquée.",
                        className="chart-subtitle",
                    ),
                    dcc.Graph(
                        id="graph-timeseries",
                        figure=build_timeseries(df_ts),
                        config={"displayModeBar": False},
                    ),
                ],
            ),

            # ── Section 4 : Tableau de données ──────────────────────────────
            html.Div(
                className="card",
                children=[
                    html.H3("Données détaillées"),
                    html.P(
                        className="chart-subtitle",
                    ),
                    html.Div(
                        className="table-controls",
                        children=[
                            dcc.Input(
                                id="input-search",
                                type="text",
                                placeholder="Rechercher une ville...",
                                debounce=True,
                                className="search-input",
                            ),
                        ],
                    ),
                    html.Div(id="table-container", className="table-wrapper"),
                ],
            ),
        ],
    )
