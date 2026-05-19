"""
generate_sample_data.py
-----------------------
Génère des données d'exemple réalistes pour les villes françaises :
  - Aménagements cyclables (longueur par ville)
  - Accidents de la route impliquant des cyclistes
  - Coordonnées géographiques des villes

Ces données sont basées sur des statistiques réelles mais synthétisées
pour garantir la disponibilité du dashboard sans connexion.
Sources de référence :
  - Baromètre des villes cyclables FUB 2021
  - Bilan de l'accidentalité ONISR 2022
"""

import pandas as pd
import numpy as np
import json
import os

SEED = 42
np.random.seed(SEED)

# Données de référence pour les grandes villes françaises
# (ville, dept, pop, lat, lon, score_cyclable_ref, acc_velo_ref)
VILLES_REF = [
    ("Strasbourg", "67", 285905, 48.5734, 7.7521, 9.2, 120),
    ("Bordeaux", "33", 257068, 44.8378, -0.5792, 8.1, 95),
    ("Grenoble", "38", 158454, 45.1885, 5.7245, 8.8, 88),
    ("Nantes", "44", 320732, 47.2184, -1.5536, 7.9, 102),
    ("Lyon", "69", 522228, 45.7640, 4.8357, 7.2, 180),
    ("Montpellier", "34", 295542, 43.6117, 3.8777, 6.8, 115),
    ("Toulouse", "31", 493465, 43.6047, 1.4442, 5.5, 142),
    ("Rennes", "35", 221272, 48.1147, -1.6794, 8.4, 90),
    ("Paris", "75", 2145906, 48.8566, 2.3522, 7.8, 750),
    ("Marseille", "13", 870018, 43.2965, 5.3698, 3.2, 195),
    ("Lille", "59", 236234, 50.6292, 3.0573, 6.5, 130),
    ("Nice", "06", 342669, 43.7102, 7.2620, 4.1, 105),
    ("Metz", "57", 116429, 49.1193, 6.1727, 6.2, 55),
    ("Dijon", "21", 155090, 47.3220, 5.0415, 7.0, 68),
    ("Clermont-Ferrand", "63", 147865, 45.7772, 3.0870, 5.0, 60),
    ("Le Mans", "72", 143599, 47.9960, 0.1966, 5.8, 58),
    ("Aix-en-Provence", "13", 143097, 43.5298, 5.4474, 3.8, 62),
    ("Brest", "29", 139674, 48.3904, -4.4861, 6.1, 52),
    ("Tours", "37", 136565, 47.3941, 0.6848, 6.6, 70),
    ("Amiens", "80", 133827, 49.8941, 2.2957, 5.9, 64),
    ("Limoges", "87", 132175, 45.8336, 1.2611, 4.5, 48),
    ("Angers", "49", 156327, 47.4784, -0.5632, 7.3, 72),
    ("Reims", "51", 185411, 49.2583, 4.0317, 5.7, 82),
    ("Le Havre", "76", 170147, 49.4944, 0.1079, 4.8, 75),
    ("Saint-Étienne", "42", 171961, 45.4347, 4.3922, 4.2, 65),
    ("Toulon", "83", 176198, 43.1242, 5.9280, 3.6, 80),
    ("Rouen", "76", 112321, 49.4432, 1.0999, 5.4, 58),
    ("Nancy", "54", 104069, 48.6921, 6.1844, 6.0, 52),
    ("Caen", "14", 107229, 49.1829, -0.3707, 5.8, 50),
    ("Orléans", "45", 116326, 47.9029, 1.9039, 6.3, 55),
    ("Mulhouse", "68", 110359, 47.7508, 7.3359, 7.5, 65),
    ("Besançon", "25", 117392, 47.2378, 6.0241, 6.9, 58),
    ("Perpignan", "66", 121875, 42.6976, 2.8954, 3.9, 52),
    ("Boulogne-Billancourt", "92", 121334, 48.8352, 2.2400, 7.6, 85),
    ("Saint-Denis", "93", 111103, 48.9356, 2.3539, 5.1, 78),
    ("Versailles", "78", 85771, 48.8014, 2.1301, 6.8, 42),
    ("Argenteuil", "95", 113474, 48.9472, 2.2467, 4.8, 68),
    ("Montreuil", "93", 109584, 48.8641, 2.4483, 6.4, 72),
    ("Nîmes", "30", 151075, 43.8367, 4.3601, 4.2, 65),
    ("Villeurbanne", "69", 151447, 45.7665, 4.8794, 7.0, 78),
    ("Pau", "64", 77130, 43.2951, -0.3708, 5.2, 38),
    ("La Rochelle", "17", 79690, 46.1591, -1.1520, 8.0, 42),
    ("Avignon", "84", 94787, 43.9493, 4.8055, 4.6, 48),
    ("Poitiers", "86", 91784, 46.5802, 0.3404, 5.7, 42),
    ("Chambéry", "73", 60438, 45.5646, 5.9178, 6.5, 32),
    ("Bayonne", "64", 52859, 43.4933, -1.4748, 5.8, 28),
    ("Colmar", "68", 68702, 48.0794, 7.3580, 7.2, 38),
    ("Lorient", "56", 58693, 47.7483, -3.3671, 6.3, 30),
    ("Quimper", "29", 63479, 47.9960, -4.0972, 5.5, 30),
    ("Arras", "62", 42512, 50.2921, 2.7817, 5.6, 22),
    ("Évreux", "27", 49755, 49.0237, 1.1513, 4.7, 24),
    ("Belfort", "90", 47491, 47.6390, 6.8630, 6.0, 28),
    ("Troyes", "10", 60750, 48.2973, 4.0745, 5.1, 30),
    ("Calais", "62", 73901, 50.9513, 1.8587, 4.3, 35),
    ("Dunkerque", "59", 91386, 51.0343, 2.3773, 5.0, 42),
    ("Valence", "26", 64260, 44.9333, 4.8922, 5.5, 32),
    ("Chartres", "28", 40029, 48.4469, 1.4874, 5.3, 20),
    ("Bourges", "18", 62247, 47.0810, 2.3988, 5.2, 30),
    ("La Roche-sur-Yon", "85", 55408, 46.6703, -1.4267, 5.9, 28),
    ("Vannes", "56", 55272, 47.6559, -2.7605, 6.2, 28),
]

def generate_villes_data() -> pd.DataFrame:
    """
    Génère un DataFrame structuré pour chaque ville avec :
    - km_pistes_cyclables : longueur totale des pistes cyclables (km)
    - km_voirie_totale : longueur totale de voirie (km)
    - proportion_cyclable : ratio km_pistes / km_voirie (%)
    - nb_accidents_velo : nombre d'accidents impliquant au moins un cycliste
    - nb_accidents_total : nombre d'accidents toutes catégories
    - taux_accidents_velo : nb_accidents_velo / population * 100000
    """
    rows = []
    for ville, dept, pop, lat, lon, score_ref, acc_ref in VILLES_REF:
        # Longueur de voirie proportionnelle à la population (empirique)
        km_voirie = pop / 1000 * np.random.uniform(0.8, 1.2) * 2.5

        # Proportion cyclable corrélée négativement au score (villes moins cyclables = moins de pistes)
        # score_ref va de ~3 à ~9
        pct_cyclable = (score_ref / 10) * np.random.uniform(0.85, 1.15) * 0.12  # max ~11%
        km_pistes = km_voirie * pct_cyclable

        # Accidents vélo corrélés à la population et inversement au score
        coeff_accident = (10 - score_ref) / 10  # plus c'est cyclable, moins il y a d'acc
        nb_acc_velo = int(acc_ref * np.random.uniform(0.85, 1.15))
        nb_acc_total = int(nb_acc_velo * np.random.uniform(4, 8))

        # Taux pour 100 000 habitants
        taux_acc_velo = nb_acc_velo / pop * 100000

        rows.append({
            "ville": ville,
            "departement": dept,
            "population": pop,
            "latitude": lat,
            "longitude": lon,
            "km_pistes_cyclables": round(km_pistes, 1),
            "km_voirie_totale": round(km_voirie, 1),
            "proportion_cyclable": round(pct_cyclable * 100, 2),
            "nb_accidents_velo": nb_acc_velo,
            "nb_accidents_total": nb_acc_total,
            "taux_accidents_velo": round(taux_acc_velo, 2),
            "score_cyclable": score_ref,
        })

    df = pd.DataFrame(rows)
    return df


def generate_accidents_timeseries() -> pd.DataFrame:
    """
    Génère une série temporelle d'accidents vélo par ville et par année (2015-2023).
    Montre la tendance : les villes qui investissent dans les pistes cyclables
    voient leur accidentalité baisser.
    """
    rows = []
    for ville, dept, pop, lat, lon, score_ref, acc_ref_2023 in VILLES_REF:
        for year in range(2015, 2024):
            # Tendance à la baisse pour les villes avec bon score cyclable
            trend = 1 - (score_ref / 10) * 0.03 * (year - 2015)
            noise = np.random.uniform(0.9, 1.1)
            nb_acc = max(5, int(acc_ref_2023 * trend * noise))
            rows.append({
                "ville": ville,
                "annee": year,
                "nb_accidents_velo": nb_acc,
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    raw_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
    cleaned_dir = os.path.join(os.path.dirname(__file__), "data", "cleaned")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(cleaned_dir, exist_ok=True)

    df_villes = generate_villes_data()
    df_villes.to_csv(os.path.join(raw_dir, "villes_sample.csv"), index=False)
    print(f"[sample] villes_sample.csv généré ({len(df_villes)} villes)")

    df_ts = generate_accidents_timeseries()
    df_ts.to_csv(os.path.join(raw_dir, "accidents_timeseries_sample.csv"), index=False)
    print(f"[sample] accidents_timeseries_sample.csv généré ({len(df_ts)} lignes)")
