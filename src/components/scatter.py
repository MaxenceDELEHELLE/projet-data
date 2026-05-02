"""
scatter.py
----------
Composant : nuage de points montrant la corrélation entre
proportion de voies cyclables et taux d'accidents vélo.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


TEMPLATE = "plotly_white"
PALETTE = {
    "< 2 %":  "#e63946",
    "2–5 %":  "#f4a261",
    "5–8 %":  "#2a9d8f",
    "> 8 %":  "#264653",
}


def build_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Construit un nuage de points avec régression linéaire.

    Axes :
      - X : proportion de voies cyclables (%)
      - Y : taux d'accidents vélo (pour 100 000 hab.)
      - Taille : population

    Paramètres
    ----------
    df : DataFrame nettoyé

    Retourne
    --------
    go.Figure
    """
    fig = go.Figure()

    # ── Traces par catégorie ─────────────────────────────────────────────────
    for cat, color in PALETTE.items():
        sub = df[df["categorie_cyclable"] == cat]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["proportion_cyclable"],
                y=sub["taux_accidents_velo"],
                mode="markers",
                name=cat,
                marker=dict(
                    size=sub["marker_size"] * 1.3,
                    color=color,
                    opacity=0.8,
                    line=dict(width=0.8, color="white"),
                    sizemode="diameter",
                ),
                customdata=sub[["ville", "nb_accidents_velo", "population", "km_pistes_cyclables"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Proportion cyclable : %{x:.1f} %<br>"
                    "Taux accidents : %{y:.1f} / 100 000 hab.<br>"
                    "Accidents vélo : %{customdata[1]}<br>"
                    "Population : %{customdata[2]:,}<br>"
                    "Pistes : %{customdata[3]:.0f} km<extra></extra>"
                ),
            )
        )

    # ── Ligne de régression ──────────────────────────────────────────────────
    x = df["proportion_cyclable"].values
    y = df["taux_accidents_velo"].values
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() >= 2:
        coefs = np.polyfit(x[mask], y[mask], 1)
        x_reg = np.linspace(x[mask].min(), x[mask].max(), 100)
        y_reg = np.polyval(coefs, x_reg)
        # Calcul R²
        y_pred = np.polyval(coefs, x[mask])
        ss_res = np.sum((y[mask] - y_pred) ** 2)
        ss_tot = np.sum((y[mask] - y[mask].mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        slope_txt = "positive" if coefs[0] > 0 else "négative"
        fig.add_trace(
            go.Scatter(
                x=x_reg,
                y=y_reg,
                mode="lines",
                line=dict(color="#6c757d", width=2, dash="dash"),
                name=f"Tendance (R²={r2:.2f})",
                hoverinfo="skip",
            )
        )

        # Annotation R²
        fig.add_annotation(
            x=x_reg[-1],
            y=y_reg[-1],
            text=f"R² = {r2:.2f}",
            showarrow=False,
            font=dict(size=12, color="#6c757d"),
            xanchor="left",
            xshift=8,
        )

    # ── Mise en page ─────────────────────────────────────────────────────────
    fig.update_layout(
        template=TEMPLATE,
        height=480,
        margin=dict(l=60, r=40, t=20, b=60),
        xaxis=dict(
            title="Proportion de voies cyclables (% de la voirie)",
            showgrid=True,
            gridcolor="#e9ecef",
            ticksuffix=" %",
        ),
        yaxis=dict(
            title="Taux d'accidents vélo (pour 100 000 hab.)",
            showgrid=True,
            gridcolor="#e9ecef",
        ),
        legend=dict(
            title="Infrastructure cyclable",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="right",
            x=1,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
    )

    return fig
