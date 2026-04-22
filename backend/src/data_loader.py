import os
import meteostat as ms
import pandas as pd

def fetch_weather_data(lat, lon, alt, start_date, end_date, output_path):
    """
    Extrage date de la Meteostat folosind ID-ul stației pentru acuratețe maximă.
    """
    # Folosim direct ID-ul stației București / Băneasa în loc de coordonate (lat/lon)
    station_id = '15420'
    print(f"Descărcare date pentru stația meteo București (ID: {station_id})...")
    
    try:
        # Preluarea datelor zilnice folosind ID-ul stației
        ts = ms.daily(station_id, start_date, end_date)
        
        # Compatibilitate cu noua versiune Meteostat
        if hasattr(ts, 'fetch'):
            df = ts.fetch()
        else:
            df = ts 
            
    except Exception as e:
        print(f"Eroare la conectarea cu Meteostat: {e}")
        return

    # Verificăm dacă df este invalid sau gol
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        print("EROARE: Nu s-au putut descărca datele nici pentru stația oficială.")
        return
        
    # Salvare în format CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path)
    print(f"Datele au fost salvate cu succes în: {output_path}")