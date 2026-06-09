import os
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
        # Lecture du CSV distant avec Pandas
        df = pd.read_csv(
            url,
            sep=None,          # Détection automatique du séparateur
            engine="python",
            on_bad_lines="skip"
        )

        if df.empty:
            print("[get_data] AVERTISSEMENT : DataFrame vide reçu depuis Koumoul.")
            return False

        # Connexion à SQLite et sauvegarde
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
    Télécharge les aménagements cyclables IDF (data.iledefrance.fr).
    Retourne True si succès ou fichier déjà présent, False sinon.
    """
    ensure_dir(RAW_DIR)

    if os.path.exists(CYCLABLE_GEOJSON):
        print(f"[get_data] Fichier déjà présent : {CYCLABLE_GEOJSON}")
        return True

    url = (
        "https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/"
        "amenagements-velo-en-ile-de-france0/exports/csv"
        "?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    )
    print(f"[get_data] Téléchargement aménagements cyclables...")
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(CYCLABLE_GEOJSON, "wb") as f:
            f.write(r.content)
        print(f"[get_data] Sauvegardé : {CYCLABLE_GEOJSON}")
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

    departements = ["75", "77", "78", "91", "92", "93", "94", "95"]
    all_features = []
    errors = []

    for dep in departements:
        url = f"https://geo.api.gouv.fr/communes?codeDepartement={dep}&format=geojson"
        print(f"[get_data] Dép {dep}...")
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

    if errors:
        print(f"[get_data] AVERTISSEMENT : départements en échec : {errors}")

    geojson = {
        "type": "FeatureCollection",
        "features": all_features
    }

    with open(COMMUNES_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    print(f"[get_data] OK communes : {len(all_features)} features ({len(departements) - len(errors)}/{len(departements)} dép réussis)")
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