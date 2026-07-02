import pandas as pd
import requests
import time
import calendar

print("🥷 Abordarea  activată: Descărcăm datele lună cu lună (Micro-Chunking)...")
print("Acest proces va dura aproximativ 6-8 minute. Poți lăsa terminalul să ruleze în fundal.\n")

toate_datele = []

# Iterăm prin fiecare an (2014 - 2023)
for an in range(2014, 2024):
    # Iterăm prin fiecare lună (1 - 12)
    for luna in range(1, 13):
        
        ultima_zi = calendar.monthrange(an, luna)[1]
        
        # Formatăm datele (ex: 2014-01-01 și 2014-01-31)
        start_date = f"{an}-{luna:02d}-01"
        end_date = f"{an}-{luna:02d}-{ultima_zi:02d}"
        
        print(f"📥 Descarc perioada: {start_date} -> {end_date}...")
        
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": 44.4268,
            "longitude": 26.1025,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,precipitation",
            "timezone": "auto"
        }
        
        try:
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                df_luna = pd.DataFrame(data['hourly'])
                toate_datele.append(df_luna)
            else:
                print(f"⚠️ Eroare de la satelit pentru {start_date}: Cod {response.status_code}")
                
        except Exception as e:
            print(f"❌ Timeout/Eroare de rețea la {start_date}. Trecem mai departe. Detalii: {e}")
            
        
        time.sleep(3)

print("\n✅ Toate descărcările au fost finalizate! Începe unificarea și curățarea...")

if len(toate_datele) > 0:
    
    df_complet = pd.concat(toate_datele, ignore_index=True)
    
   
    df_complet['date'] = pd.to_datetime(df_complet['time']).dt.date
    df_complet['month'] = pd.to_datetime(df_complet['time']).dt.month
    
   
    df_daily = df_complet.groupby('date').agg({
        'month': 'first',
        'temperature_2m': ['min', 'max', 'mean'],
        'relative_humidity_2m': 'mean',
        'surface_pressure': 'mean',
        'precipitation': 'sum'
    }).reset_index()
    
    
    df_daily.columns = ['date', 'month', 'tmin', 'tmax', 'tavg', 'humidity', 'pressure', 'prcp']
    
   
    df_daily = df_daily.dropna(axis=0)
    
    
    df_daily.to_csv("data/processed/weather_clean.csv", index=False)
    
    print(f"🎉 EXCELENT! Noul set de date a fost salvat și conține {len(df_daily)} zile reale!")
    print("Senzorii de Presiune și Umiditate sunt acum compleți. Poți porni serverul API!")
else:
    print("❌ Nu s-a putut descărca nimic. Verifică conexiunea.")