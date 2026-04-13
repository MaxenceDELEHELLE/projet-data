import pandas as pd
import numpy as np
from config import RAW_DATA_PATH, CLEANED_DATA_PATH

def prepare_bike_data():
    # Lecture avec le bon délimiteur (souvent ',' ou ';' pour les fichiers BAAC)
    df = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    
    # Nettoyage des coordonnées (on remplace les virgules par des points)
    df['lat'] = pd.to_numeric(df['lat'].astype(str).str.replace(',', '.'), errors='coerce')
    df['long'] = pd.to_numeric(df['long'].astype(str).str.replace(',', '.'), errors='coerce')
    
    # On enlève les points sans coordonnées
    df = df.dropna(subset=['lat', 'long'])
    
    # Conversion de l'année en entier
    df['an'] = pd.to_numeric(df['an'], errors='coerce')
    
    # Simulation d'une colonne "Taille Ville" si elle n'existe pas (pour le filtre)
    # Dans un vrai projet, on ferait une jointure avec le fichier des aménagements
    if 'population' not in df.columns:
        df['taille_ville'] = np.random.choice(['Petite', 'Moyenne', 'Grande'], len(df))

    df.to_csv(CLEANED_DATA_PATH, index=False)
    return df