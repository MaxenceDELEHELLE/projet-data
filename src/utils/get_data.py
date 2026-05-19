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
VILLES_CLEAN_PATH = os.path.join(RAW_DIR, "villes_clean.csv")

def ensure_dir(path: str) -> None:
    """Crée le répertoire s'il n'existe pas."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"[get_data] Répertoire créé : {path}")

def fetch_accidents_velo_sqlite():
    """
    Télécharge les accidents vélos (Koumoul) et les injecte dans SQLite.
    Source : OpenData Koumoul
    """
    ensure_dir(RAW_DIR)
    url = "https://opendata.koumoul.com/data-fair/api/v1/datasets/accidents-velos/raw"
    
    print(f"[get_data] Chargement des accidents vélos depuis Koumoul...")
    try:
        # Lecture du CSV distant avec Pandas
        df = pd.read_csv(
            url,
            sep=None,         # Détection automatique du séparateur
            engine="python",
            on_bad_lines="skip"
        )
        
        # Connexion à SQLite et sauvegarde
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("data", conn, if_exists="replace", index=False)
        conn.close()
        
        print(f"[get_data] Succès : {len(df)} lignes stockées dans {DB_PATH}")
    except Exception as e:
        print(f"[get_data] Erreur accidents vélos (Koumoul) : {e}")

def fetch_accidents_gouv():
    """Télécharge les caractéristiques accidents 2023 (Data.gouv)."""
    ensure_dir(RAW_DIR)
    if os.path.exists(ACCIDENTS_CSV):
        print(f"[get_data] Fichier déjà présent : {ACCIDENTS_CSV}")
        return

    url = "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2023/20241028-103125/caract-2023.csv"
    print(f"[get_data] Téléchargement accidents 2023...")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(ACCIDENTS_CSV, "wb") as f:
            f.write(r.content)
        print(f"[get_data] Sauvegardé : {ACCIDENTS_CSV}")
    except Exception as e:
        print(f"[get_data] Erreur accidents 2023 : {e}")

def fetch_cycling_infra():
    """Télécharge les aménagements cyclables IDF (Transport.data.gouv)."""
    ensure_dir(RAW_DIR)
    if os.path.exists(CYCLABLE_GEOJSON):
        print(f"[get_data] Fichier déjà présent : {CYCLABLE_GEOJSON}")
        return

    url = "https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/amenagements-velo-en-ile-de-france0/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    print(f"[get_data] Téléchargement aménagements cyclables...")
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(CYCLABLE_GEOJSON, "wb") as f:
            f.write(r.content)
        print(f"[get_data] Sauvegardé : {CYCLABLE_GEOJSON}")
    except Exception as e:
        print(f"[get_data] Erreur cyclable : {e}")

def fetch_communes_geojson():
    """Télécharge les communes d'Île-de-France (Geo API)."""

    ensure_dir(RAW_DIR)

    if os.path.exists(COMMUNES_GEOJSON):
        print(f"[get_data] Fichier déjà présent : {COMMUNES_GEOJSON}")
        return

    departements = ["75", "77", "78", "91", "92", "93", "94", "95"]

    all_features = []

    for dep in departements:

        url = (
            f"https://geo.api.gouv.fr/departements/"
            f"{dep}/communes"
            f"?format=geojson&geometry=centre"
        )

        print(f"[get_data] Téléchargement département {dep}...")

        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()

            geojson = r.json()

            if "features" in geojson:
                all_features.extend(geojson["features"])

        except Exception as e:
            print(f"[get_data] Erreur département {dep} : {e}")

    final_geojson = {
        "type": "FeatureCollection",
        "features": all_features
    }

    with open(COMMUNES_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(final_geojson, f, ensure_ascii=False)

    print(f"[get_data] Sauvegardé : {COMMUNES_GEOJSON}")
    print(f"[get_data] Nombre de communes : {len(all_features)}")

if __name__ == "__main__":
    print("--- DÉBUT DE LA RÉCUPÉRATION DES DONNÉES ---")
    
    # 1. Données réelles spécifiques (SQLite)
    fetch_accidents_velo_sqlite()
    
    # 2. Données générales (Fichiers bruts)
    fetch_accidents_gouv()
    fetch_cycling_infra()
    fetch_communes_geojson()
    
    print("\n[get_data] Terminé ! Toutes les données sont dans :", RAW_DIR)