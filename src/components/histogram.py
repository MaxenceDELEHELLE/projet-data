"""
histogram.py
------------
Composant : histogramme des villes classées par proportion de voies cyclables.
Coloré par catégorie cyclable, avec superposition du taux d'accidents.
"""

import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots


# Palette cohérente avec le thème du dashboard
PALETTE = {
    "< 2 %":  "#e63946",
    "2–5 %":  "#f4a261",
    "5–8 %":  "#2a9d8f",
    "> 8 %":  "#264653",
}

TEMPLATE = "plotly_white"


def build_histogram(df: pd.DataFrame, top_n: int = 40) -> go.Figure:
    """
    Construit un graphique en barres horizontales classant les villes
    par proportion de voies cyclables (décroissant).

    Paramètres
    ----------
    df : DataFrame nettoyé (issu de clean_data.run_cleaning)
    top_n : nombre de villes à afficher (défaut 40)

    Retourne
    --------
    go.Figure
    """
    df_plot = df.head(top_n).copy()

    # Couleur selon la catégorie
    colors = df_plot["categorie_cyclable"].map(PALETTE).tolist()

    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.65, 0.35],
        subplot_titles=[
            "Proportion de voies cyclables (% de la voirie)",
            "Taux d'accidents vélo (pour 100 000 hab.)",
        ],
        shared_yaxes=True,
        horizontal_spacing=0.04,
    )

    # ── Barres : proportion cyclable ────────────────────────────────────────
    fig.add_trace(
        go.Bar(
            y=df_plot["ville"],
            x=df_plot["proportion_cyclable"],
            orientation="h",
            marker_color=colors,
            text=df_plot["proportion_cyclable"].apply(lambda v: f"{v:.1f} %"),
            textposition="outside",
            name="% voies cyclables",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Proportion cyclable : %{x:.1f} %<br>"
                "Pistes : %{customdata[0]:.0f} km<br>"
                "Voirie totale : %{customdata[1]:.0f} km<extra></extra>"
            ),
            customdata=df_plot[["km_pistes_cyclables", "km_voirie_totale"]].values,
        ),
        row=1, col=1,
    )

    # ── Barres : taux d'accidents ────────────────────────────────────────────
    fig.add_trace(
        go.Bar(
            y=df_plot["ville"],
            x=df_plot["taux_accidents_velo"],
            orientation="h",
            marker_color=colors,
            marker_opacity=0.7,
            text=df_plot["taux_accidents_velo"].apply(lambda v: f"{v:.1f}"),
            textposition="outside",
            name="Taux d'accidents",
            showlegend=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Taux : %{x:.1f} acc./100 000 hab.<br>"
                "Total accidents vélo : %{customdata[0]}<extra></extra>"
            ),
            customdata=df_plot[["nb_accidents_velo"]].values,
        ),
        row=1, col=2,
    )

    # ── Légende manuelle ────────────────────────────────────────────────────
    for label, color in PALETTE.items():
        fig.add_trace(
            go.Bar(
                x=[None], y=[None],
                orientation="h",
                marker_color=color,
                name=f"Infra cyclable : {label}",
                showlegend=True,
            )
        )

    # ── Mise en page ────────────────────────────────────────────────────────
    height = max(500, top_n * 22)
    fig.update_layout(
        template=TEMPLATE,
        height=height,
        margin=dict(l=130, r=60, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        barmode="overlay",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12),
    )

    fig.update_xaxes(title_text="% voies cyclables", row=1, col=1, showgrid=True, gridcolor="#e9ecef")
    fig.update_xaxes(title_text="Accidents / 100 000 hab.", row=1, col=2, showgrid=True, gridcolor="#e9ecef")
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=11))

    return fig
