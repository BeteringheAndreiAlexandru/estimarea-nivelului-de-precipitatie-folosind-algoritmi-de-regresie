from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import requests
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ORASE_COORDONATE = {
    "București": {"lat": 44.4268, "lon": 26.1025},
    "Cluj-Napoca": {"lat": 46.7712, "lon": 23.5901},
    "Timișoara": {"lat": 45.7489, "lon": 21.2087},
    "Iași": {"lat": 47.1585, "lon": 27.6014},
    "Constanța": {"lat": 44.1792, "lon": 28.6498},
    "Brașov": {"lat": 45.6427, "lon": 25.5887}
}

# --- 1. ANTRENAREA ȘI OPTIMIZAREA MODELULUI ---
print("Se inițializează antrenarea modelului...")
try:
    df = pd.read_csv("data/processed/weather_clean.csv")
    features_ideale = ['month', 'tavg', 'tmin', 'tmax']
    active_features = [col for col in features_ideale if col in df.columns]
    target = 'prcp'

    df = df.dropna(subset=active_features + [target])
    X = df[active_features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # AI OPTIMIZAT (Hyperparameter Tuning)
    model = RandomForestRegressor(
        n_estimators=200,       # 200 de arbori in loc de 100 pentru o decizie mai stabila
        max_depth=10,           # Previne supraspecializarea (overfitting)
        min_samples_split=5,    # Regula mai stricta pentru crearea noilor frunze
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Calcularea metodelor de evaluare pentru Licență
    predictii_test = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictii_test)
    r2 = r2_score(y_test, predictii_test)
    
    print(f"✅ Modelul a învățat din {len(df)} zile folosind: {active_features}")
    print(f"📊 PERFORMANȚĂ MODEL: Eroare medie (MAE): {mae:.2f} mm | Scorul R²: {r2:.2f}")
except Exception as e:
    print(f"❌ EROARE la încărcarea datelor: {e}")

class WeatherData(BaseModel):
    month: int
    tavg: float
    tmin: float
    tmax: float

# --- 3. RUTA PENTRU PREDICȚIE MANUALĂ ---
@app.post("/predict")
def predict_manual(data: WeatherData):
    input_dict = {
        'month': [data.month],
        'tavg': [data.tavg],
        'tmin': [data.tmin],
        'tmax': [data.tmax]
    }
    input_df = pd.DataFrame(input_dict)[active_features]
    raw_prediction = model.predict(input_df)[0]
    final_prediction = float(max(0, round(raw_prediction, 2)))
    return {"estimated_precipitation_mm": final_prediction}

# --- 4. RUTA PENTRU PROGNOZA LIVE PE 7 ZILE ---
@app.get("/forecast-7-days")
def get_live_forecast(oras: str = "București"):
    if oras not in ORASE_COORDONATE:
        return {"error": "Orașul nu este suportat."}
        
    lat = ORASE_COORDONATE[oras]["lat"]
    lon = ORASE_COORDONATE[oras]["lon"]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&hourly=temperature_2m&timezone=auto"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": "Nu s-au putut prelua datele de la Open-Meteo."}
            
        meteo_json = response.json()
        daily = meteo_json['daily']
        hourly = meteo_json['hourly']
        
        rezultate_7_zile = []
        for i in range(len(daily['time'])):
            data_calendar = daily['time'][i]
            tmin = daily['temperature_2m_min'][i]
            tmax = daily['temperature_2m_max'][i]
            luna = datetime.strptime(data_calendar, "%Y-%m-%d").month
            
            start_idx = i * 24
            end_idx = start_idx + 24
            ore_brute = hourly['time'][start_idx:end_idx]
            temp_ore = hourly['temperature_2m'][start_idx:end_idx]
            ore_formatate = [ora[-5:] for ora in ore_brute]

            input_row = {
                'month': [luna],
                'tavg': [(tmin + tmax) / 2],
                'tmin': [tmin],
                'tmax': [tmax]
            }
            input_df = pd.DataFrame(input_row)[active_features]
            pred_ai = float(max(0, round(model.predict(input_df)[0], 2)))
            
            rezultate_7_zile.append({
                "data": data_calendar,
                "tmin": tmin,
                "tmax": tmax,
                "ploaie_estimata_mm": pred_ai,
                "grafic_ore": ore_formatate,
                "grafic_temperaturi": temp_ore
            })
            
        return {"prognoza": rezultate_7_zile}
    except Exception as e:
        return {"error": f"Problemă tehnică: {str(e)}"}

# --- 5. RUTA PENTRU XAI (TRANSPARENȚA MODELULUI) ---
@app.get("/feature-importance")
def get_feature_importance():
    try:
        importances = model.feature_importances_
        importance_dict = {
            feature: float(round(imp * 100, 2)) 
            for feature, imp in zip(active_features, importances)
        }
        return importance_dict
    except Exception as e:
        return {"error": str(e)}