"""
config.py
---------
Fichier de configuration centralisé du projet.
Modifiez les chemins et paramètres ici sans toucher au reste du code.
"""

import os

# ── Répertoires ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")

# ── Fichiers de données ───────────────────────────────────────────────────────
VILLES_CLEAN_PATH = os.path.join(CLEANED_DIR, "villes_clean.csv")
TIMESERIES_CLEAN_PATH = os.path.join(CLEANED_DIR, "timeseries_clean.csv")

# Données brutes d'exemple (fallback si téléchargement impossible)
VILLES_SAMPLE_PATH = os.path.join(RAW_DIR, "villes_sample.csv")
TIMESERIES_SAMPLE_PATH = os.path.join(RAW_DIR, "accidents_timeseries_sample.csv")

# ── Serveur Dash ─────────────────────────────────────────────────────────────
HOST = "127.0.0.1"
PORT = 8050
DEBUG = False

# ── Paramètres graphiques ────────────────────────────────────────────────────
DEFAULT_TOP_N = 40          # Nombre de villes dans l'histogramme par défaut
MAP_CENTER_LAT = 46.5
MAP_CENTER_LON = 2.5