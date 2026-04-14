import os
import sqlite3
import pandas as pd

CSV_URL = "https://opendata.koumoul.com/data-fair/api/v1/datasets/accidents-velos/raw"
DB_PATH = "data/raw/accidentsVelo.db"
TABLE_NAME = "data"

def main_get_data():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    print("downloading csv...")

    df = pd.read_csv(
        CSV_URL,
        sep=None,
        engine="python",
        on_bad_lines="skip"
    )

    print("NB lignes:", len(df))
    print("columns:", df.columns)

    conn = sqlite3.connect(DB_PATH)

    try:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        print("success")
    finally:
        conn.close()

if __name__ == "__main__":
    main_get_data()