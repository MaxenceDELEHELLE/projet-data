from dash import dcc, html
import plotly.express as px
import pandas as pd
import sqlite3
from config import RAW_DATA_PATH_ACCIDENTS_SQL

TABLE_NAME = "data"

def create_map():
    conn = sqlite3.connect(RAW_DATA_PATH_ACCIDENTS_SQL)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()

    df["lat"] = pd.to_numeric(df["lat"].astype(str).str.replace(",", "."), errors="coerce")
    df["long"] = pd.to_numeric(df["long"].astype(str).str.replace(",", "."), errors="coerce")
    df = df.dropna(subset=["lat", "long"])

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="long",
        color="grav" if "grav" in df.columns else None,
        zoom=5,
        height=700,
        mapbox_style="carto-positron",
        hover_data=df.columns
    )

    fig.update_layout(
        margin=dict(r=0, t=0, l=0, b=0),
        paper_bgcolor="#0e1117",
        font=dict(color="white")
    )

    return html.Div([
        html.H1("🚲 Accidents vélo en France", style={"textAlign": "center"}),
        dcc.Graph(figure=fig)
    ])

def create_histogram():
    conn = sqlite3.connect(RAW_DATA_PATH_ACCIDENTS_SQL)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()

    if "annee" in df.columns:
        year_col = "annee"
    elif "year" in df.columns:
        year_col = "year"
    else:
        return html.Div("Pas de colonne année dans les données")

    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df = df.dropna(subset=[year_col])

    agg = df.groupby(year_col).size().reset_index(name="count")

    fig = px.bar(
        agg,
        x=year_col,
        y="count",
        title="Nombre d'accidents par année"
    )

    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white")
    )

    return html.Div([
        html.H1("Accidents par année", style={"textAlign": "center"}),
        dcc.Graph(figure=fig)
    ])

def layout():
    return html.Div([
        html.H1("Dashboard Accidents Vélo", style={"textAlign": "center"}),

        dcc.Tabs([
            dcc.Tab(label="🗺️ Carte", children=[create_map()]),
            dcc.Tab(label="📊 Statistiques", children=[create_histogram()])
        ])
    ])