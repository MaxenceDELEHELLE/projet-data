"""
map_chart.py
------------
Composant : carte choroplèthe / bulles géolocalisées des villes françaises.
Montre simultanément :
  - la taille des bulles → nombre d'accidents vélo
  - la couleur → proportion de voies cyclables
"""

import plotly.graph_objects as go
import pandas as pd


TEMPLATE = "plotly_white"


def build_map(df: pd.DataFrame) -> go.Figure:
    """
    Construit une carte à bulles centrée sur la France.

    La taille des bulles est proportionnelle au nombre d'accidents vélo ;
    la couleur encode la proportion de voies cyclables.

    Paramètres
    ----------
    df : DataFrame nettoyé (issu de clean_data.run_cleaning)

    Retourne
    --------
    go.Figure
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lat=df["latitude"],
            lon=df["longitude"],
            text=df["ville"],
            mode="markers+text",
            textposition="top center",
            textfont=dict(size=9, color="#333"),
            marker=dict(
                size=df["marker_size"],
                color=df["proportion_cyclable"],
                colorscale=[
                    [0.0, "#e63946"],
                    [0.3, "#f4a261"],
                    [0.6, "#2a9d8f"],
                    [1.0, "#264653"],
                ],
                showscale=True,
                colorbar=dict(
                    title=dict(text="% voies cyclables", side="right"),
                    thickness=14,
                    len=0.7,
                    ticksuffix=" %",
                ),
                opacity=0.85,
                line=dict(width=0.5, color="white"),
                sizemode="diameter",
                sizeref=1,
            ),
            customdata=df[
                ["ville", "proportion_cyclable", "nb_accidents_velo",
                 "taux_accidents_velo", "population", "km_pistes_cyclables"]
            ].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Proportion cyclable : %{customdata[1]:.1f} %<br>"
                "Pistes cyclables : %{customdata[5]:.0f} km<br>"
                "Accidents vélo : %{customdata[2]}<br>"
                "Taux : %{customdata[3]:.1f} / 100 000 hab.<br>"
                "Population : %{customdata[4]:,}<extra></extra>"
            ),
            name="",
        )
    )

    fig.update_layout(
        template=TEMPLATE,
        height=560,
        margin=dict(l=0, r=0, t=10, b=0),
        geo=dict(
            scope="europe",
            center=dict(lat=46.5, lon=2.5),
            projection_scale=6,
            showland=True,
            landcolor="#f8f9fa",
            showcoastlines=True,
            coastlinecolor="#dee2e6",
            showcountries=True,
            countrycolor="#adb5bd",
            showframe=False,
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        annotations=[
            dict(
                text=(
                    "Taille des bulles proportionnelle au nombre d'accidents vélo · "
                    "Couleur = proportion de voies cyclables"
                ),
                xref="paper", yref="paper",
                x=0.5, y=-0.02,
                showarrow=False,
                font=dict(size=10, color="#6c757d"),
                align="center",
            )
        ],
    )

    return fig
