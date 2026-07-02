import pandas as pd

print("⏳ Se citește fișierul descărcat manual...")

try:
    df_orare = pd.read_csv("date_brute.csv", skiprows=3)
except FileNotFoundError:
    print("❌ EROARE: Nu găsesc fișierul 'date_brute.csv'. Asigură-te că l-ai mutat în folderul backend!")
    exit()


df_orare.columns = ['time', 'temperature', 'humidity', 'precipitation', 'pressure']

print("⚙️ Se grupează datele (Data Aggregation)...")
df_orare['date'] = pd.to_datetime(df_orare['time']).dt.date
df_orare['month'] = pd.to_datetime(df_orare['time']).dt.month


df_zilnic = df_orare.groupby('date').agg({
    'month': 'first',
    'temperature': ['min', 'max', 'mean'],
    'humidity': 'mean',
    'pressure': 'mean',
    'precipitation': 'sum'
}).reset_index()


df_zilnic.columns = ['date', 'month', 'tmin', 'tmax', 'tavg', 'humidity', 'pressure', 'prcp']


df_zilnic = df_zilnic.dropna()
df_zilnic.to_csv("data/processed/weather_clean.csv", index=False)

print(f"🎉 GATA! Setul de date cu {len(df_zilnic)} zile reale a fost curățat și salvat cu succes!")