from dash import html

# On définit une variable 'layout'
layout = html.Div([
    html.H1("🚲 Observatoire des Accidents de Vélo"),
    html.P("Analyse de la sécurité cyclable en fonction des infrastructures."),
    html.Hr(),
    html.A("Accéder à la carte interactive", href="/map")
])