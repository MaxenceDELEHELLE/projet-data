"""
clean_data.py
-------------
Nettoie et enrichit les données brutes pour le dashboard.
"""

import os
import sqlite3
import json

import pandas as pd
import numpy as np

# ── Chemins ───────────────────────────────────────────────────────────────────
_HERE       = os.path.dirname(os.path.abspath(__file__))
RAW_DIR     = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "raw"))
CLEANED_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "cleaned"))

DB_PATH          = os.path.join(RAW_DIR, "accidentsVelo.db")
CYCLABLE_PATH    = os.path.join(RAW_DIR, "amenagements_cyclables.geojson")
COMMUNES_GEOJSON = os.path.join(RAW_DIR, "communes_idf.geojson")

VILLES_SAMPLE_PATH     = os.path.join(RAW_DIR, "villes_sample.csv")
TIMESERIES_SAMPLE_PATH = os.path.join(RAW_DIR, "accidents_timeseries_sample.csv")

MOIS_FR = {
    "janvier": "01", "février": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
}


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


# ── Chargement ────────────────────────────────────────────────────────────────

def load_accidents_sqlite() -> pd.DataFrame:
    """
    Colonnes réelles : dep, com (code INSEE 5 car.), an, mois (texte FR), grav, …
    com contient déjà le code INSEE complet → utilisé directement.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"[clean_data] Base SQLite introuvable : {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM data", conn)
    conn.close()
    print(f"[clean_data] SQLite : {len(df)} lignes chargées.")

    df["code_insee"] = df["com"].astype(str).str.strip().str.zfill(5)
    df["annee"]      = pd.to_numeric(df["an"], errors="coerce")
    df["mois_num"]   = (
        df["mois"].astype(str).str.strip().str.lower()
        .map(MOIS_FR)
        .fillna("00")
    )
    df["mois_periode"] = df["an"].astype(str).str.strip() + "-" + df["mois_num"]

    return df


def load_cycling_infra() -> pd.DataFrame:
    if not os.path.exists(CYCLABLE_PATH):
        raise FileNotFoundError(f"[clean_data] Fichier cyclable introuvable : {CYCLABLE_PATH}")
    df = pd.read_csv(CYCLABLE_PATH, sep=";", on_bad_lines="skip")
    print(f"[clean_data] Cyclable : {len(df)} lignes chargées.")
    return df


def load_communes() -> pd.DataFrame:
    if not os.path.exists(COMMUNES_GEOJSON):
        raise FileNotFoundError(f"[clean_data] GeoJSON communes introuvable : {COMMUNES_GEOJSON}")

    with open(COMMUNES_GEOJSON, encoding="utf-8") as f:
        geojson = json.load(f)

    rows = []
    for feat in geojson.get("features", []):
        props  = feat.get("properties", {})
        geom   = feat.get("geometry", {})
        coords = geom.get("coordinates") if geom else None

        lat, lon = None, None
        if coords:
            gtype = geom.get("type", "")
            if gtype == "Point":
                lon, lat = coords[0], coords[1]
            elif gtype == "Polygon":
                ring = coords[0]
                lon  = np.mean([c[0] for c in ring])
                lat  = np.mean([c[1] for c in ring])
            elif gtype == "MultiPolygon":
                ring = coords[0][0]
                lon  = np.mean([c[0] for c in ring])
                lat  = np.mean([c[1] for c in ring])

        rows.append({
            "code_insee":  str(props.get("code", "")).zfill(5),
            "nom_commune": props.get("nom"),
            "departement": props.get("codeDepartement"),
            "latitude":    lat,
            "longitude":   lon,
            "population":  props.get("population"),
        })

    df = pd.DataFrame(rows)
    print(f"[clean_data] Communes : {len(df)} lignes chargées.")
    return df


# ── Fusion ────────────────────────────────────────────────────────────────────

def _find_col(df: pd.DataFrame, candidates: list) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def build_villes(
    df_accidents: pd.DataFrame,
    df_cyclable:  pd.DataFrame,
    df_communes:  pd.DataFrame,
) -> pd.DataFrame:

    # ── 1. Accidents par code INSEE ───────────────────────────────────────────
    acc_agg = (
        df_accidents
        .groupby("code_insee", as_index=False)
        .size()
        .rename(columns={"size": "nb_accidents_velo"})
    )

    # ── 2. Pistes cyclables par code INSEE ────────────────────────────────────
    code_col = _find_col(df_cyclable, [
        "insee_com", "code_insee", "code_commune", "codecommune",
        "com_insee", "codinsee", "code_com",
    ])
    len_col = _find_col(df_cyclable, [
        "longueur", "length", "lon_tronc", "long_tronc",
        "longueur_m", "longueur_km", "km",
    ])

    if code_col and len_col:
        df_cyc = df_cyclable[[code_col, len_col]].copy()
        df_cyc[code_col] = df_cyc[code_col].astype(str).str.strip().str.zfill(5)
        df_cyc[len_col]  = pd.to_numeric(df_cyc[len_col], errors="coerce").fillna(0)
        cyc_agg = (
            df_cyc.groupby(code_col, as_index=False)[len_col]
            .sum()
            .rename(columns={code_col: "code_insee", len_col: "km_pistes_cyclables"})
        )
        if cyc_agg["km_pistes_cyclables"].median() > 500:
            cyc_agg["km_pistes_cyclables"] = (cyc_agg["km_pistes_cyclables"] / 1000).round(3)
    else:
        print(f"[clean_data] AVERT : colonnes cyclable introuvables "
              f"(code={code_col}, longueur={len_col}). Colonnes : {list(df_cyclable.columns)}")
        cyc_agg = pd.DataFrame(columns=["code_insee", "km_pistes_cyclables"])

    # ── 3. Fusion ─────────────────────────────────────────────────────────────
    df = (
        df_communes
        .merge(acc_agg, on="code_insee", how="left")
        .merge(cyc_agg, on="code_insee", how="left")
    )

    df["nb_accidents_velo"]   = df["nb_accidents_velo"].fillna(0).astype(int)
    df["km_pistes_cyclables"] = df["km_pistes_cyclables"].fillna(0).round(3)
    df["population"]          = pd.to_numeric(df["population"], errors="coerce").fillna(0).astype(int)

    # ── 4. Indicateurs dérivés ────────────────────────────────────────────────
    df["taux_accidents_velo"] = np.where(
        df["population"] > 0,
        (df["nb_accidents_velo"] / df["population"] * 100_000).round(2),
        0.0,
    )
    df["proportion_cyclable"] = np.where(
        df["population"] > 0,
        (df["km_pistes_cyclables"] / df["population"] * 10_000).round(4),
        0.0,
    )
    # Proxy voirie totale : ~6 m de voirie par habitant (moyenne française)
    df["km_voirie_totale"] = (df["population"] * 6 / 1000).round(1)

    df = df.rename(columns={"nom_commune": "ville"})
    return df


# ── Nettoyage final ───────────────────────────────────────────────────────────

def clean_villes(df: pd.DataFrame) -> pd.DataFrame:
    cols_required = ["ville", "latitude", "longitude", "population"]
    df = df.dropna(subset=cols_required).copy()
    df = df[df["population"] > 0].copy()

    bins   = [0, 2, 5, 8, float("inf")]
    labels = ["< 2 %", "2–5 %", "5–8 %", "> 8 %"]
    df["categorie_cyclable"] = pd.cut(
        df["proportion_cyclable"], bins=bins, labels=labels, right=False
    )
    df["marker_size"] = np.sqrt(df["population"] / 1000).round(1)
    df = df.sort_values("proportion_cyclable", ascending=False).reset_index(drop=True)
    return df


def build_timeseries(df_accidents: pd.DataFrame, df_villes: pd.DataFrame) -> pd.DataFrame:
    """
    Série temporelle par année et par ville.
    Colonnes produites (attendues par timeseries.py) :
      annee, ville, nb_accidents_velo, categorie_cyclable, proportion_cyclable
    """
    df = df_accidents.copy()

    # Résolution code_insee → ville (IDF uniquement)
    code_to_ville = df_villes.set_index("code_insee")["ville"].to_dict()
    df["ville"] = df["code_insee"].map(code_to_ville)
    df = df.dropna(subset=["ville", "annee"])

    if df.empty:
        print("[clean_data] AVERT : aucun accident ne correspond aux communes IDF.")
        return pd.DataFrame(columns=[
            "annee", "ville", "nb_accidents_velo",
            "categorie_cyclable", "proportion_cyclable",
        ])

    # Agrégation par année + ville
    ts = (
        df.groupby(["annee", "ville"], as_index=False)
        .size()
        .rename(columns={"size": "nb_accidents_velo"})
    )
    ts["annee"] = ts["annee"].astype(int)

    ts = ts.merge(
        df_villes[["ville", "categorie_cyclable", "proportion_cyclable"]],
        on="ville", how="left",
    )
    return ts.dropna(subset=["categorie_cyclable"])


# ── Pipeline principal ────────────────────────────────────────────────────────

def run_cleaning() -> tuple[pd.DataFrame, pd.DataFrame]:
    ensure_dir(CLEANED_DIR)

    try:
        df_accidents = load_accidents_sqlite()
        df_cyclable  = load_cycling_infra()
        df_communes  = load_communes()

        df_villes_raw = build_villes(df_accidents, df_cyclable, df_communes)
        df_villes     = clean_villes(df_villes_raw)
        df_ts         = build_timeseries(df_accidents, df_villes)

        print(f"[clean_data] ✅ {len(df_villes)} villes, {len(df_ts)} lignes TS.")

    except Exception as e:
        print(f"[clean_data] ⚠️  Erreur ({type(e).__name__}: {e})")
        print("[clean_data] Bascule sur les données d'exemple...")

        if not os.path.exists(VILLES_SAMPLE_PATH) or not os.path.exists(TIMESERIES_SAMPLE_PATH):
            raise FileNotFoundError(
                "Données réelles ET données d'exemple introuvables. "
                "Exécutez generate_sample_data.py ou get_data.py."
            )

        df_villes = clean_villes(pd.read_csv(VILLES_SAMPLE_PATH))
        df_ts_raw = pd.read_csv(TIMESERIES_SAMPLE_PATH)
        df_ts = df_ts_raw.merge(
            df_villes[["ville", "categorie_cyclable", "proportion_cyclable"]],
            on="ville", how="left"
        ).dropna(subset=["categorie_cyclable"])

    out_villes = os.path.join(CLEANED_DIR, "villes_clean.csv")
    out_ts     = os.path.join(CLEANED_DIR, "timeseries_clean.csv")

    df_villes.to_csv(out_villes, index=False)
    df_ts.to_csv(out_ts,        index=False)

    print(f"[clean_data] Sauvegardé : {out_villes}")
    print(f"[clean_data] Sauvegardé : {out_ts}")

    return df_villes, df_ts


if __name__ == "__main__":
    run_cleaning()