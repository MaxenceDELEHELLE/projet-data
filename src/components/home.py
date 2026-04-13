from dash import html
from src.components.navbar import create_navbar

def layout():
    return html.Div([
        create_navbar(),
        html.H2("Analyse des accidents de vélo"),
        html.P("Bienvenue sur l'outil d'analyse spatiale des risques cyclables.")
    ])