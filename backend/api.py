from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import requests
from datetime import datetime
import custom_rf  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ORASE = {
    "București": {"lat": 44.4323, "lon": 26.1063},
    "Cluj-Napoca": {"lat": 46.7712, "lon": 23.6236},
    "Timișoara": {"lat": 45.7489, "lon": 21.2087},
    "Iași": {"lat": 47.1585, "lon": 27.6014},
    "Constanța": {"lat": 44.1792, "lon": 28.6498},
    "Brașov": {"lat": 45.6427, "lon": 25.5887}
}

model_cpp = None

class WeatherInput(BaseModel):
    month: int
    tavg: float
    tmin: float
    tmax: float
    humidity: float
    pressure: float

@app.on_event("startup")
def startup_event():
    global model_cpp
    print("\n====== PORNIRE SERVER ======")
    print("1. Incarcam datele istorice...")
    
    try:
        df = pd.read_csv("data/processed/weather_clean.csv")
        X = df[['month', 'tavg', 'tmin', 'tmax', 'humidity', 'pressure']].values.tolist()
        
        col_tinta = 'precipitation' if 'precipitation' in df.columns else df.columns[-1]
        y = df[col_tinta].values.tolist()
        
        print("2. Antrenam motorul C++ Custom Random Forest...")
        model_cpp = custom_rf.CustomRandomForest(n_estimators=15, max_depth=10)
        model_cpp.fit(X, y)
        print("3. Model antrenat si gata de actiune!\n============================")
        
    except Exception as e:
        print(f"ATENTIE: Eroare la incarcarea fisierului CSV: {e}")

@app.post("/predict")
def predict_weather(data: WeatherInput):
    input_data = [[data.month, data.tavg, data.tmin, data.tmax, data.humidity, data.pressure]]
    prediction = model_cpp.predict(input_data)[0]
    result = max(0.0, round(prediction, 2))
    return {"estimated_precipitation_mm": result}

@app.get("/forecast-7-days")
def get_live_forecast(oras: str):
    if oras not in ORASE:
        return {"error": "Orașul nu există în baza de date."}
        
    lat = ORASE[oras]["lat"]
    lon = ORASE[oras]["lon"]
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,surface_pressure&timezone=auto"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        ore = data["hourly"]["time"]
        temperaturi = data["hourly"]["temperature_2m"]
        umiditati = data["hourly"]["relative_humidity_2m"]
        presiuni = data["hourly"]["surface_pressure"]
        
        zile_dict = {}
        for i in range(len(ore)):
            data_zi = ore[i].split("T")[0]
            ora_exacta = ore[i].split("T")[1]
            t = temperaturi[i]
            h = umiditati[i]
            p = presiuni[i]
            
            if data_zi not in zile_dict:
                zile_dict[data_zi] = {
                    "t_list": [], "h_list": [], "p_list": [],
                    "ore_list": [], "temp_grafic": []
                }
            
            zile_dict[data_zi]["t_list"].append(t)
            zile_dict[data_zi]["h_list"].append(h)
            zile_dict[data_zi]["p_list"].append(p)
            zile_dict[data_zi]["ore_list"].append(ora_exacta)
            zile_dict[data_zi]["temp_grafic"].append(t)

        prognoza_finala = []
        for data_zi, valori in list(zile_dict.items())[:7]:
            tmin = min(valori["t_list"])
            tmax = max(valori["t_list"])
            tavg = sum(valori["t_list"]) / len(valori["t_list"])
            h_avg = sum(valori["h_list"]) / len(valori["h_list"])
            p_avg = sum(valori["p_list"]) / len(valori["p_list"])
            luna = int(data_zi.split("-")[1])
            
            input_cpp = [[luna, tavg, tmin, tmax, h_avg, p_avg]]
            pred_mm = model_cpp.predict(input_cpp)[0]
            
            prognoza_finala.append({
                "data": data_zi,
                "tmin": round(tmin, 1),
                "tmax": round(tmax, 1),
                "ploaie_estimata_mm": max(0.0, round(pred_mm, 2)),
                "grafic_ore": valori["ore_list"],
                "grafic_temperaturi": valori["temp_grafic"]
            })
            
        return {"prognoza": prognoza_finala}
    except Exception as e:
        return {"error": str(e)}

@app.get("/feature-importance")
def get_feature_importance():
    # 🌟 NOU: Cerem procentele de la modelul C++ compilat
    importances = model_cpp.get_feature_importances()
    
    # Mapăm scorurile la coloanele noastre în ordinea exactă în care le-am trimis la antrenare
    return {
        "month": round(importances[0], 2),
        "tavg": round(importances[1], 2),
        "tmin": round(importances[2], 2),
        "tmax": round(importances[3], 2),
        "humidity": round(importances[4], 2),
        "pressure": round(importances[5], 2)
    }