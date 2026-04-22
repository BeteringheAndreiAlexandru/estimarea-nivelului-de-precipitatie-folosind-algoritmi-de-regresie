from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import requests
from datetime import datetime

app = FastAPI()

# Configurăm CORS: Permitem paginii tale web (Frontend) să vorbească cu acest cod Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. ANTRENAREA MODELULUI ---
print("Se inițializează antrenarea modelului...")

try:
    df = pd.read_csv("data/processed/weather_clean.csv")

    # Identificăm coloanele disponibile (evităm eroarea dacă lipsește tavg)
    features_ideale = ['month', 'tavg', 'tmin', 'tmax']
    active_features = [col for col in features_ideale if col in df.columns]
    target = 'prcp'

    # Curățăm rândurile goale
    df = df.dropna(subset=active_features + [target])

    X = df[active_features]
    y = df[target]

    # Împărțim datele pentru antrenare și testare
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Antrenăm algoritmul Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print(f"✅ Succes! Modelul a învățat din {len(df)} zile folosind: {active_features}")

except Exception as e:
    print(f"❌ EROARE la încărcarea datelor: {e}")

# --- 2. DEFINIREA FORMATULUI DE DATE ---
class WeatherData(BaseModel):
    month: int
    tavg: float
    tmin: float
    tmax: float

# --- 3. RUTA PENTRU PREDICȚIE MANUALĂ (BUTONUL ALBASTRU) ---
@app.post("/predict")
def predict_manual(data: WeatherData):
    # Pregătim datele primite de la utilizator
    input_dict = {
        'month': [data.month],
        'tavg': [data.tavg],
        'tmin': [data.tmin],
        'tmax': [data.tmax]
    }
    
    # Filtrăm doar coloanele pe care le știe modelul
    input_df = pd.DataFrame(input_dict)[active_features]
    
    # Facem predicția și o transformăm în float standard (pentru JavaScript)
    raw_prediction = model.predict(input_df)[0]
    final_prediction = float(max(0, round(raw_prediction, 2)))
    
    return {"estimated_precipitation_mm": final_prediction}

# --- 4. RUTA PENTRU PROGNOZA LIVE PE 7 ZILE (BUTONUL VERDE) ---
@app.get("/forecast-7-days")
def get_live_forecast():
    # Coordonatele pentru București
    lat, lon = 44.4268, 26.1025
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": "Nu s-au putut prelua datele de la Open-Meteo."}
            
        meteo_json = response.json()
        daily = meteo_json['daily']
        
        rezultate_7_zile = []
        
        for i in range(len(daily['time'])):
            data_calendar = daily['time'][i]
            tmin = daily['temperature_2m_min'][i]
            tmax = daily['temperature_2m_max'][i]
            luna = datetime.strptime(data_calendar, "%Y-%m-%d").month
            
            # Pregătim inputul pentru AI
            input_row = {
                'month': [luna],
                'tavg': [(tmin + tmax) / 2],
                'tmin': [tmin],
                'tmax': [tmax]
            }
            input_df = pd.DataFrame(input_row)[active_features]
            
            # Predicția AI transformată în float standard
            pred_ai = float(max(0, round(model.predict(input_df)[0], 2)))
            
            rezultate_7_zile.append({
                "data": data_calendar,
                "tmin": tmin,
                "tmax": tmax,
                "ploaie_estimata_mm": pred_ai
            })
            
        return {"prognoza": rezultate_7_zile}

    except Exception as e:
        return {"error": f"Problemă tehnică: {str(e)}"}