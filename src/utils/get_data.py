import os
import io
import requests
import sqlite3
import pandas as pd
import json

# --- Configuration des chemins ---
# On définit le dossier racine par rapport à l'emplacement du script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "data", "raw"))

# Chemins des fichiers de sortie
DB_PATH = os.path.join(RAW_DIR, "accidentsVelo.db")
ACCIDENTS_CSV = os.path.join(RAW_DIR, "accidents_2023.csv")
CYCLABLE_GEOJSON = os.path.join(RAW_DIR, "amenagements_cyclables.geojson")
COMMUNES_GEOJSON = os.path.join(RAW_DIR, "communes_idf.geojson")
VILLES_CLEAN_PATH = os.path.join(RAW_DIR, "villes_clean_1.csv")


def ensure_dir(path: str) -> None:
    """Crée le répertoire s'il n'existe pas."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"[get_data] Répertoire créé : {path}")


def fetch_accidents_velo_sqlite() -> bool:
    """
    Télécharge les accidents vélos (Koumoul) et les injecte dans SQLite.
    Source : OpenData Koumoul
    Retourne True si succès, False sinon.
    """
    ensure_dir(RAW_DIR)
    url = "https://opendata.koumoul.com/data-fair/api/v1/datasets/accidents-velos/raw"

    print(f"[get_data] Chargement des accidents vélos depuis Koumoul...")
    try:
        df = pd.read_csv(
            url,
            sep=None,
            engine="python",
            on_bad_lines="skip"
        )

        if df.empty:
            print("[get_data] AVERTISSEMENT : DataFrame vide reçu depuis Koumoul.")
            return False

        conn = sqlite3.connect(DB_PATH)
        df.to_sql("data", conn, if_exists="replace", index=False)
        conn.close()

        print(f"[get_data] Succès : {len(df)} lignes stockées dans {DB_PATH}")
        return True

    except Exception as e:
        print(f"[get_data] ERREUR accidents vélos (Koumoul) : {type(e).__name__} – {e}")
        return False


def fetch_accidents_gouv() -> bool:
    """
    Télécharge les caractéristiques accidents 2023 (Data.gouv).
    Retourne True si succès ou fichier déjà présent, False sinon.
    """
    ensure_dir(RAW_DIR)

    if os.path.exists(ACCIDENTS_CSV):
        print(f"[get_data] Fichier déjà présent : {ACCIDENTS_CSV}")
        return True

    url = (
        "https://static.data.gouv.fr/resources/"
        "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere"
        "-annees-de-2005-a-2023/20241028-103125/caract-2023.csv"
    )
    print(f"[get_data] Téléchargement accidents 2023...")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(ACCIDENTS_CSV, "wb") as f:
            f.write(r.content)
        print(f"[get_data] Sauvegardé : {ACCIDENTS_CSV}")
        return True

    except Exception as e:
        print(f"[get_data] ERREUR accidents 2023 : {type(e).__name__} – {e}")
        return False


def fetch_cycling_infra() -> bool:
    """
    Télécharge les aménagements cyclables France métropolitaine.
    Source : Base Nationale des Aménagements Cyclables (Geovelo / transport.data.gouv.fr)
    Fichier Parquet converti en CSV pour compatibilité avec clean_data.py.
    Retourne True si succès ou fichier déjà présent, False sinon.
    """
    ensure_dir(RAW_DIR)

    if os.path.exists(CYCLABLE_GEOJSON):
        print(f"[get_data] Fichier déjà présent : {CYCLABLE_GEOJSON}")
        return True

    # Base Nationale des Aménagements Cyclables — France métropolitaine (Geovelo / transport.data.gouv.fr)
    url = "https://www.data.gouv.fr/api/1/datasets/r/7b2746c8-c2fa-44e7-b171-a317e633b9c9"

    # Ancienne API IDF uniquement (conservée en commentaire) :
    # url = (
    #     "https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/"
    #     "amenagements-velo-en-ile-de-france0/exports/csv"
    #     "?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    # )

    print(f"[get_data] Téléchargement aménagements cyclables France...")
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        df = pd.read_parquet(io.BytesIO(r.content))
        # Sauvegarde en CSV avec séparateur ";" pour compatibilité avec clean_data.py
        df.to_csv(CYCLABLE_GEOJSON, index=False, sep=";")
        print(f"[get_data] Sauvegardé : {len(df)} lignes dans {CYCLABLE_GEOJSON}")
        return True

    except Exception as e:
        print(f"[get_data] ERREUR cyclable : {type(e).__name__} – {e}")
        return False


def fetch_communes_geojson() -> bool:
    """
    Télécharge les communes IDF depuis geo.api.gouv.fr.
    Retourne True si succès ou fichier déjà présent, False sinon.
    """
    ensure_dir(RAW_DIR)

    if os.path.exists(COMMUNES_GEOJSON):
        print("[get_data] Déjà présent : communes_idf.geojson")
        return True

    # Tous les départements métropolitains + DOM
    departements = (
        [str(i).zfill(2) for i in range(1, 96) if i != 20]  # 01 → 95 sauf 20
        + ["2A", "2B"]                                         # Corse
        + ["971", "972", "973", "974", "976"]                  # DOM
    )

    all_features = []
    errors = []

    for dep in departements:
        url = f"https://geo.api.gouv.fr/communes?codeDepartement={dep}&fields=nom,code,codeDepartement,population&format=geojson"
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            data = r.json()

            if isinstance(data, dict) and "features" in data:
                all_features.extend(data["features"])
            elif isinstance(data, list):
                all_features.extend(data)

        except Exception as e:
            print(f"[get_data] ERREUR dép {dep} : {type(e).__name__} – {e}")
            errors.append(dep)

    if not all_features:
        print("[get_data] ERREUR : aucune commune récupérée.")
        return False

    def get_pop(f):
        return f.get("properties", {}).get("population") or 0

    top60 = sorted(
        [f for f in all_features if get_pop(f) > 0],
        key=get_pop,
        reverse=True,
    )[:60]

    geojson = {"type": "FeatureCollection", "features": top60}

    with open(COMMUNES_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    print(f"[get_data] OK communes : {len(top60)} features ({len(departements) - len(errors)}/{len(departements)} dép réussis)")
    return True


def fetch_all() -> dict:
    """
    Lance toutes les récupérations et retourne un bilan.
    Retourne un dict { nom_source: bool } indiquant le succès de chaque appel.
    """
    results = {
        "accidents_velo_sqlite": fetch_accidents_velo_sqlite(),
        "accidents_gouv":        fetch_accidents_gouv(),
        "cycling_infra":         fetch_cycling_infra(),
        "communes_geojson":      fetch_communes_geojson(),
    }

    successes = sum(results.values())
    total = len(results)
    print(f"\n[get_data] Bilan : {successes}/{total} sources récupérées avec succès.")

    for name, ok in results.items():
        status = "✅" if ok else "❌"
        print(f"  {status}  {name}")

    return results


if __name__ == "__main__":
    print("--- DÉBUT DE LA RÉCUPÉRATION DES DONNÉES ---")
    fetch_all()
    print(f"\n[get_data] Terminé ! Toutes les données sont dans : {RAW_DIR}")