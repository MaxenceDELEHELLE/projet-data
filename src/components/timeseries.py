"""
timeseries.py
-------------
Composant : évolution temporelle du nombre d'accidents vélo (2015–2023)
regroupé par catégorie d'infrastructure cyclable.
"""

import plotly.graph_objects as go
import pandas as pd


TEMPLATE = "plotly_white"
PALETTE = {
    "< 2 %":  "#e63946",
    "2–5 %":  "#f4a261",
    "5–8 %":  "#2a9d8f",
    "> 8 %":  "#264653",
}


def build_timeseries(df_ts: pd.DataFrame) -> go.Figure:
    """
    Construit un graphique linéaire montrant l'évolution des accidents
    agrégés par catégorie d'infrastructure cyclable.

    Paramètres
    ----------
    df_ts : DataFrame timeseries nettoyé

    Retourne
    --------
    go.Figure
    """
    # Agrégation : moyenne des accidents par catégorie et par année
    agg = (
        df_ts.groupby(["annee", "categorie_cyclable"])["nb_accidents_velo"]
        .mean()
        .reset_index()
        .rename(columns={"nb_accidents_velo": "accidents_moyen"})
    )

    fig = go.Figure()

    for cat, color in PALETTE.items():
        sub = agg[agg["categorie_cyclable"] == cat].sort_values("annee")
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["annee"],
                y=sub["accidents_moyen"],
                mode="lines+markers",
                name=cat,
                line=dict(color=color, width=2.5),
                marker=dict(size=6, color=color),
                hovertemplate=(
                    f"<b>Infra : {cat}</b><br>"
                    "Année : %{x}<br>"
                    "Accidents moyens : %{y:.1f}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        template=TEMPLATE,
        height=380,
        margin=dict(l=60, r=40, t=20, b=60),
        xaxis=dict(
            title="Année",
            dtick=1,
            showgrid=True,
            gridcolor="#e9ecef",
        ),
        yaxis=dict(
            title="Accidents vélo (moyenne par ville)",
            showgrid=True,
            gridcolor="#e9ecef",
        ),
        legend=dict(
            title="Infrastructure cyclable",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        hovermode="x unified",
    )

    return fig
