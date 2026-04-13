from dash import html

def create_navbar():
    return html.Nav([
        html.H1("BikeSafe Analytics"),
        html.Div([
            html.A("Accueil", href="/"),
            html.A("Carte Interactive", href="/map"),
            html.A("Analyse", href="/analytics"),
        ], className="nav-links")
    ])