import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_PATH_ACCIDENTS = os.path.join(DATA_DIR, "raw", "accidentsVelo.csv")
CLEANED_DATA_PATH = os.path.join(DATA_DIR, "cleaned", "cleaneddata.csv")

COLORS = {
    'primary': '#1f77b4',
    'accent': '#ff7f0e',
    'background': '#f9f9f9'
}