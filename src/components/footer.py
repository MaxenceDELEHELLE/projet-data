"""
footer.py
---------
Composant : pied de page du dashboard.
"""

from dash import html


def build_footer() -> html.Div:
    """Retourne le composant pied de page."""
    return html.Div(
        className="footer",
        children=[
            html.P(
                [
                    "Sources : ",
                    html.A(
                        "Baromètre des villes cyclables FUB",
                        href="https://barometre.parlons-velo.fr/",
                        target="_blank",
                    ),
                    " · ",
                    html.A(
                        "ONISR – Bilan de l'accidentalité",
                        href="https://www.securite-routiere.gouv.fr/les-medias/nos-publications/bilan-de-laccidentalite-de-lannee-2023",
                        target="_blank",
                    ),
                    " · ",
                    html.A(
                        "data.gouv.fr",
                        href="https://www.data.gouv.fr/",
                        target="_blank",
                    ),
                ]
            ),
            html.P("Dashboard éducatif — données à titre illustratif"),
        ],
    )
