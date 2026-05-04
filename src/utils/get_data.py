"""
get_data.py
-----------
Récupère les données depuis les APIs publiques :
  - Données d'accidents corporels de la route (data.gouv.fr)
  - Données d'aménagements cyclables (transport.data.gouv.fr)

Les données brutes sont stockées dans data/raw/.
"""

import os
import requests
import json

# Répertoire de stockage des données brutes
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")


def ensure_dir(path: str) -> None:
    """Crée le répertoire s'il n'existe pas."""
    os.makedirs(path, exist_ok=True)


def fetch_accidents() -> str:
    """
    Télécharge les caractéristiques des accidents corporels depuis data.gouv.fr.
    Source : https://www.data.gouv.fr/fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2023/
    Retourne le chemin du fichier sauvegardé.
    """
    ensure_dir(RAW_DIR)
    dest = os.path.join(RAW_DIR, "accidents_2023.csv")
    if os.path.exists(dest):
        print(f"[get_data] Fichier accidents déjà présent : {dest}")
        return dest

    url = "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2023/20231231-135545/carcteristiques-2023.csv"
    print(f"[get_data] Téléchargement des accidents depuis {url} ...")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        print(f"[get_data] Accidents sauvegardés dans {dest}")
    except Exception as e:
        print(f"[get_data] Erreur téléchargement accidents : {e}")
    return dest


def fetch_cycling_infra() -> str:
    """
    Télécharge les données d'aménagements cyclables depuis transport.data.gouv.fr.
    Source : https://transport.data.gouv.fr/datasets/amenagements-cyclables-france-metropolitaine
    Retourne le chemin du fichier sauvegardé.
    """
    ensure_dir(RAW_DIR)
    dest = os.path.join(RAW_DIR, "amenagements_cyclables.geojson")
    if os.path.exists(dest):
        print(f"[get_data] Fichier cyclable déjà présent : {dest}")
        return dest

    url = "https://data.hub.iledefrance.fr/api/explore/v2.1/catalog/datasets/amenagements_cyclables_idf/exports/geojson?limit=10000"
    print(f"[get_data] Téléchargement des aménagements cyclables...")
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        print(f"[get_data] Aménagements cyclables sauvegardés dans {dest}")
    except Exception as e:
        print(f"[get_data] Erreur téléchargement cyclable : {e}")
    return dest


def fetch_communes_geojson() -> str:
    """
    Télécharge le GeoJSON simplifié des communes françaises (Île-de-France).
    Retourne le chemin du fichier sauvegardé.
    """
    ensure_dir(RAW_DIR)
    dest = os.path.join(RAW_DIR, "communes_idf.geojson")
    if os.path.exists(dest):
        print(f"[get_data] GeoJSON communes déjà présent : {dest}")
        return dest

    url = "https://geo.api.gouv.fr/departements/75,77,78,91,92,93,94,95/communes?format=geojson&geometry=centre"
    print(f"[get_data] Téléchargement des communes IDF...")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        print(f"[get_data] Communes sauvegardées dans {dest}")
    except Exception as e:
        print(f"[get_data] Erreur téléchargement communes : {e}")
    return dest


if __name__ == "__main__":
    fetch_accidents()
    fetch_cycling_infra()
    fetch_communes_geojson()
    print("[get_data] Toutes les données brutes ont été récupérées.")
