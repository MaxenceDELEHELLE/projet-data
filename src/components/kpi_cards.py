"""
kpi_cards.py
------------
Composant : cartes de KPI affichées en haut du dashboard.
"""

from dash import html
import pandas as pd


def build_kpi_cards(df: pd.DataFrame) -> html.Div:
    """
    Construit les 4 cartes de KPI résumant les données.

    Paramètres
    ----------
    df : DataFrame nettoyé des villes

    Retourne
    --------
    html.Div contenant les 4 cartes
    """
    total_villes = len(df)
    total_pistes = df["km_pistes_cyclables"].sum()
    total_accidents = df["nb_accidents_velo"].sum()
    moy_proportion = df["proportion_cyclable"].mean()

    kpis = [
        {
            "value": f"{total_villes}",
            "label": "Villes analysées",
            "icon": "🏙️",
            "color": "kpi-blue",
        },
        {
            "value": f"{total_pistes:,.0f} km",
            "label": "Pistes cyclables (total)",
            "icon": "🛣️",
            "color": "kpi-green",
        },
        {
            "value": f"{total_accidents:,}",
            "label": "Accidents vélo (2023)",
            "icon": "⚠️",
            "color": "kpi-red",
        },
        {
            "value": f"{moy_proportion:.1f} %",
            "label": "Proportion cyclable moyenne",
            "icon": "📊",
            "color": "kpi-teal",
        },
    ]

    cards = [
        html.Div(
            className=f"kpi-card {k['color']}",
            children=[
                html.Span(k["icon"], className="kpi-icon"),
                html.Div(
                    className="kpi-body",
                    children=[
                        html.Div(k["value"], className="kpi-value"),
                        html.Div(k["label"], className="kpi-label"),
                    ],
                ),
            ],
        )
        for k in kpis
    ]

    return html.Div(className="kpi-row", children=cards)
