"""
clean_data.py
-------------
Nettoie et enrichit les données brutes pour le dashboard.
  - Fusionne si besoin les sources (accidents + infra cyclable)
  - Calcule les indicateurs dérivés
  - Sauvegarde dans data/cleaned/

Si les données réelles n'ont pas pu être téléchargées,
utilise les données d'exemple pré-générées.
"""

import os
import pandas as pd
import numpy as np

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
CLEANED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cleaned")


def ensure_dir(path: str) -> None:
    """Crée le répertoire s'il n'existe pas."""
    os.makedirs(path, exist_ok=True)


def load_villes(raw_dir: str = RAW_DIR) -> pd.DataFrame:
    """
    Charge le dataset principal des villes.
    Utilise les données réelles si disponibles, sinon les données d'exemple.
    """
    # Tente de charger les données réelles mergées
    merged_path = os.path.join(raw_dir, "villes_merged.csv")
    sample_path = os.path.join(raw_dir, "villes_sample.csv")

    if os.path.exists(merged_path):
        print("[clean_data] Chargement des données réelles...")
        df = pd.read_csv(merged_path)
    elif os.path.exists(sample_path):
        print("[clean_data] Chargement des données d'exemple...")
        df = pd.read_csv(sample_path)
    else:
        raise FileNotFoundError(
            "Aucun fichier de données trouvé dans data/raw/. "
            "Exécutez d'abord generate_sample_data.py ou get_data.py."
        )
    return df


def load_timeseries(raw_dir: str = RAW_DIR) -> pd.DataFrame:
    """Charge la série temporelle des accidents."""
    path = os.path.join(raw_dir, "accidents_timeseries_sample.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    return pd.read_csv(path)


def clean_villes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et enrichit le DataFrame des villes :
    - Supprime les lignes incomplètes
    - Calcule les catégories de proportion cyclable
    - Normalise les colonnes numériques
    Retourne le DataFrame nettoyé.
    """
    # Suppression des valeurs manquantes sur les colonnes essentielles
    cols_required = [
        "ville", "latitude", "longitude", "population",
        "proportion_cyclable", "nb_accidents_velo", "taux_accidents_velo",
    ]
    df = df.dropna(subset=cols_required).copy()

    # Catégorie de proportion cyclable (pour coloration dans les graphiques)
    bins = [0, 2, 5, 8, 100]
    labels = ["< 2 %", "2–5 %", "5–8 %", "> 8 %"]
    df["categorie_cyclable"] = pd.cut(
        df["proportion_cyclable"], bins=bins, labels=labels, right=False
    )

    # Taille des marqueurs proportionnelle à la population (pour la carte)
    df["marker_size"] = np.sqrt(df["population"] / 1000).round(1)

    # Tri par proportion cyclable décroissante
    df = df.sort_values("proportion_cyclable", ascending=False).reset_index(drop=True)

    return df


def clean_timeseries(df: pd.DataFrame, df_villes: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie la série temporelle et la joint avec les données villes
    pour ajouter la catégorie cyclable.
    """
    df = df.merge(
        df_villes[["ville", "categorie_cyclable", "proportion_cyclable"]],
        on="ville",
        how="left",
    )
    return df.dropna(subset=["categorie_cyclable"])


def run_cleaning() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Exécute le pipeline de nettoyage complet.
    Sauvegarde les fichiers nettoyés dans data/cleaned/.
    Retourne (df_villes_clean, df_timeseries_clean).
    """
    ensure_dir(CLEANED_DIR)

    df_villes = clean_villes(load_villes())
    df_ts = clean_timeseries(load_timeseries(), df_villes)

    out_villes = os.path.join(CLEANED_DIR, "villes_clean.csv")
    out_ts = os.path.join(CLEANED_DIR, "timeseries_clean.csv")

    df_villes.to_csv(out_villes, index=False)
    df_ts.to_csv(out_ts, index=False)

    print(f"[clean_data] {len(df_villes)} villes nettoyées → {out_villes}")
    print(f"[clean_data] {len(df_ts)} lignes timeseries → {out_ts}")

    return df_villes, df_ts


if __name__ == "__main__":
    run_cleaning()
