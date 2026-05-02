"""
header.py
---------
Composant : en-tête du dashboard avec titre et sous-titre.
"""

from dash import html


def build_header() -> html.Div:
    """
    Retourne le composant d'en-tête du dashboard.

    Retourne
    --------
    html.Div
    """
    return html.Div(
        className="header",
        children=[
            html.Div(
                className="header-inner",
                children=[
                    html.Div(
                        className="header-icon",
                        children=["🚲"],
                    ),
                    html.Div(
                        className="header-text",
                        children=[
                            html.H1("Vélo & Sécurité Routière"),
                            html.P(
                                "Infrastructures cyclables et accidentalité en France — "
                                "données Open Data · 60 villes analysées"
                            ),
                        ],
                    ),
                ],
            )
        ],
    )
