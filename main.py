from dash import Dash, html, dcc, Input, Output
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.pages.home import layout as home_layout
from src.pages.more_complex_page.layout import create_map_layout as map_layout

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/map':
        return map_layout()
    else:
        return home_layout

if __name__ == '__main__':
    app.run(debug=True)