import pandas as pd
import os

def clean_raw_data(input_path, output_path):
    """
    Încarcă datele brute, curăță valorile lipsă (NaN) și adaugă coloane noi (an, lună).
    """
    print(f"  -> Se încarcă datele brute din {input_path}")
    
    # Încărcăm fișierul CSV salvat anterior
    df = pd.read_csv(input_path)
    
    # Ne asigurăm că formatul coloanei de timp este recunoscut ca dată calendaristică
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
        
        # Extragem anul și luna pentru a ne ajuta la analiză
        df['year'] = df['time'].dt.year
        df['month'] = df['time'].dt.month

    # Curățăm Precipitațiile (prcp). Dacă lipsește valoarea, presupunem că nu a plouat (0 mm)
    if 'prcp' in df.columns:
        df['prcp'] = df['prcp'].fillna(0)

    # Pentru temperaturi (tavg, tmin, tmax), dacă lipsește o zi, copiem valoarea din ziua precedentă (forward fill)
    cols_to_fill = ['tavg', 'tmin', 'tmax']
    for col in cols_to_fill:
        if col in df.columns:
            df[col] = df[col].ffill()

    # Aruncăm alte coloane care au prea multe date lipsă sau nu ne ajută (opțional)
    # Ex: snow (zăpadă), wdir (direcția vântului) dacă nu le folosim
    cols_to_drop = ['snow', 'tsun', 'wpgt']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

    # Salvăm datele procesate
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"  -> Datele curățate au fost salvate cu succes în {output_path}")
    
    return df