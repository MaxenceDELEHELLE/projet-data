"""
main.py
-------
Point d'entrée principal du dashboard « Vélo & Sécurité Routière ».

Lancement :
    $ python main.py

Le dashboard est accessible sur http://127.0.0.1:8050/
"""

import os
import sys
import pandas as pd

# ── Dépendances Dash ─────────────────────────────────────────────────────────
from dash import Dash, html, dcc, Input, Output, dash_table

# ── Modules du projet ────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from src.components.header import build_header
from src.components.footer import build_footer
from src.components.histogram import build_histogram
from src.components.map_chart import build_map
from src.components.scatter import build_scatter
from src.components.timeseries import build_timeseries
from src.pages.home import build_home_layout


# ── Pipeline données ─────────────────────────────────────────────────────────

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Charge les données nettoyées si disponibles en cache.
    Sinon, tente de récupérer les données réelles via get_data.py.
    En cas d'échec total, bascule sur les données d'exemple.
    Retourne (df_villes, df_timeseries).
    """

    # ── 1. Cache : données nettoyées déjà présentes ──────────────────────────
    if (
        os.path.exists(config.VILLES_CLEAN_PATH)
        and os.path.exists(config.TIMESERIES_CLEAN_PATH)
    ):
        df_villes = pd.read_csv(config.VILLES_CLEAN_PATH)
        df_ts = pd.read_csv(config.TIMESERIES_CLEAN_PATH)
        print("[main] Données nettoyées chargées depuis le cache.")
        return df_villes, df_ts

    # ── 2. Tentative de récupération des vraies données ───────────────────────
    print("[main] Pas de cache trouvé – tentative de récupération des données réelles...")
    try:
        from src.utils.get_data import fetch_all
        results = fetch_all()

        # Si aucune source n'a fonctionné, on lève une exception pour basculer
        if not any(results.values()):
            raise RuntimeError("Toutes les sources API ont échoué.")

        print("[main] Données brutes récupérées (au moins partiellement), nettoyage...")

    except Exception as e:
        print(f"[main] ⚠️  Récupération API impossible : {type(e).__name__} – {e}")
        print("[main] Bascule sur les données d'exemple...")

        # ── 3. Fallback : données d'exemple ──────────────────────────────────
        if not os.path.exists(config.VILLES_SAMPLE_PATH):
            print("[main] Génération des données d'exemple...")
            from generate_sample_data import generate_villes_data, generate_accidents_timeseries
            os.makedirs(config.RAW_DIR, exist_ok=True)
            generate_villes_data().to_csv(config.VILLES_SAMPLE_PATH, index=False)
            generate_accidents_timeseries().to_csv(config.TIMESERIES_SAMPLE_PATH, index=False)
        else:
            print("[main] Données d'exemple déjà présentes.")

    # ── 4. Nettoyage (données réelles ou d'exemple) ───────────────────────────
    print("[main] Nettoyage des données...")
    from src.utils.clean_data import run_cleaning
    df_villes, df_ts = run_cleaning()

    return df_villes, df_ts


# ── Initialisation Dash ───────────────────────────────────────────────────────

def create_app(df_villes: pd.DataFrame, df_ts: pd.DataFrame) -> Dash:
    """
    Crée et configure l'application Dash avec son layout et ses callbacks.

    Paramètres
    ----------
    df_villes : DataFrame des villes nettoyé
    df_ts     : DataFrame de la série temporelle nettoyé

    Retourne
    --------
    Dash app configurée
    """
    app = Dash(
        __name__,
        external_stylesheets=[
            "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Syne:wght@700;800&display=swap",
        ],
        title="Vélo & Sécurité Routière",
        suppress_callback_exceptions=True,
    )

    # ── Layout principal ─────────────────────────────────────────────────────
    app.layout = html.Div(
        className="app-wrapper",
        children=[
            # Stockage des données côté client pour les callbacks
            dcc.Store(id="store-villes", data=df_villes.to_dict("records")),
            dcc.Store(id="store-ts", data=df_ts.to_dict("records")),

            build_header(),

            html.Main(
                className="main-container",
                children=[build_home_layout(df_villes, df_ts)],
            ),

            build_footer(),
        ],
    )

    # ── Callbacks ────────────────────────────────────────────────────────────

    @app.callback(
        Output("graph-histogram", "figure"),
        Input("slider-top-n", "value"),
        Input("store-villes", "data"),
    )
    def update_histogram(top_n: int, data: list) -> object:
        """Met à jour l'histogramme quand le slider change."""
        df = pd.DataFrame(data)
        return build_histogram(df, top_n=top_n or 40)

    @app.callback(
        Output("graph-scatter", "figure"),
        Input("checklist-categories", "value"),
        Input("store-villes", "data"),
    )
    def update_scatter(selected_cats: list, data: list) -> object:
        """Met à jour le scatter plot selon les catégories sélectionnées."""
        df = pd.DataFrame(data)
        if selected_cats:
            df = df[df["categorie_cyclable"].isin(selected_cats)]
        return build_scatter(df)

    @app.callback(
        Output("table-container", "children"),
        Input("input-search", "value"),
        Input("store-villes", "data"),
    )
    def update_table(search: str, data: list) -> object:
        """Met à jour le tableau de données selon la recherche."""
        df = pd.DataFrame(data)

        if search:
            df = df[df["ville"].str.contains(search, case=False, na=False)]

        cols_display = [
            {"name": "Ville",       "id": "ville"},
            {"name": "Dép.",        "id": "departement"},
            {"name": "Population",  "id": "population",           "type": "numeric",
             "format": {"specifier": ",.0f"}},
            {"name": "Pistes (km)", "id": "km_pistes_cyclables",  "type": "numeric",
             "format": {"specifier": ".1f"}},
            {"name": "% cyclable",  "id": "proportion_cyclable",  "type": "numeric",
             "format": {"specifier": ".2f"}},
            {"name": "Acc. vélo",   "id": "nb_accidents_velo",    "type": "numeric"},
            {"name": "Taux /100k",  "id": "taux_accidents_velo",  "type": "numeric",
             "format": {"specifier": ".1f"}},
            {"name": "Catégorie",   "id": "categorie_cyclable"},
        ]

        return dash_table.DataTable(
            data=df.to_dict("records"),
            columns=cols_display,
            sort_action="native",
            page_size=15,
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#f8f9fa",
                "fontWeight": "600",
                "fontSize": "13px",
                "borderBottom": "2px solid #dee2e6",
            },
            style_cell={
                "fontSize": "13px",
                "padding": "10px 14px",
                "border": "none",
                "borderBottom": "1px solid #f1f3f5",
                "fontFamily": "Inter, sans-serif",
            },
            style_data_conditional=[
                {
                    "if": {"filter_query": "{categorie_cyclable} = '> 8 %'"},
                    "backgroundColor": "#d8f3ee",
                    "color": "#264653",
                },
                {
                    "if": {"filter_query": "{categorie_cyclable} = '< 2 %'"},
                    "backgroundColor": "#fde8ea",
                    "color": "#e63946",
                },
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#fafbfc",
                },
            ],
        )

    return app


# ── Point d'entrée ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df_villes, df_ts = load_data()
    app = create_app(df_villes, df_ts)
    print(f"\n🚲  Dashboard disponible sur http://{config.HOST}:{config.PORT}/\n")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)