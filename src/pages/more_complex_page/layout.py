from dash import dcc, html
import plotly.express as px
import pandas as pd
from config import RAW_DATA_PATH_ACCIDENTS


def create_map_layout():
    try:
        df = pd.read_csv(RAW_DATA_PATH_ACCIDENTS)
    except Exception:
        df = pd.DataFrame({
            'lat': [48.8566, 45.7640, 43.2965],
            'long': [2.3522, 4.8357, 5.3698],
            'grav': [1, 2, 3]
        })

    df["lat"] = df["lat"].astype(str).str.replace(",", ".")
    df["long"] = df["long"].astype(str).str.replace(",", ".")

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["long"] = pd.to_numeric(df["long"], errors="coerce")

    df = df.dropna(subset=["lat", "long", "grav"])

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="long",
        color="grav",
        hover_data=["grav"],
        zoom=5,
        height=600,
        mapbox_style="carto-positron"
    )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return html.Div([

        html.H2("Carte des accidents en France"),

        dcc.Graph(
            id="map-accidents",
            figure=fig
        )

    ])