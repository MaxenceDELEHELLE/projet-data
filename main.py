from dash import Dash, html, dcc, Input, Output
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.pages.home import layout as home_layout
from src.pages.more_complex_page.layout import create_map, create_histogram

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    html.Div([
        dcc.Link("Acceuil", href="/"),
        " | ",
        dcc.Link("Carte", href="/map"),
        " | ",
        dcc.Link("Stats", href="/stats"),
    ]),

    html.Hr(),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/map':
        return create_map()

    elif pathname == '/stats':
        return create_histogram()

    else:
        return home_layout

if __name__ == '__main__':
    app.run(debug=True)