import pandas as pd
from datetime import datetime
from src.data_loader import fetch_weather_data
from src.data_cleaning import clean_raw_data
from src.model_trainer import train_regression_model

# Coordonate București
LAT, LON, ALT = 44.4268, 26.1025, 80

# Perioada analizată
START_DATE = datetime(2018, 1, 1)
END_DATE = datetime(2023, 12, 31)

RAW_DATA_PATH = "data/raw/weather_bucharest.csv"
PROCESSED_DATA_PATH = "data/processed/weather_clean.csv"

def main():
    print("--- Începere Proiect Estimare Precipitații ---\n")

    # PASUL 1: Extragere date
    print("Pasul 1: Colectare date de la Meteostat...")
    fetch_weather_data(LAT, LON, ALT, START_DATE, END_DATE, RAW_DATA_PATH)

    # PASUL 2: Curățare date 
    print("\nPasul 2: Curățare și pregătire date...")
    df_clean = clean_raw_data(RAW_DATA_PATH, PROCESSED_DATA_PATH)

    # PASUL 3: Aplicare Regresie (Machine Learning)
    print("\nPasul 3: Antrenare algoritm de regresie...")
    model, metrics = train_regression_model(PROCESSED_DATA_PATH)
    
    print("\n✅ --- PROIECT FINALIZAT --- ✅")
    print(f"Eroarea medie absolută (MAE): {metrics['MAE']} mm")
    print(f"Acest lucru înseamnă că, în medie, modelul nostru greșește cu {metrics['MAE']} litri pe metru pătrat atunci când prezice ploaia.")

if __name__ == "__main__":
    main()