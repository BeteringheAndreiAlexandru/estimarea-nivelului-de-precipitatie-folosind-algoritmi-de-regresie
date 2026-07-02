import pandas as pd
import numpy as np
from datetime import timedelta, date

print("⏳ Generăm date meteorologice sintetice pentru antrenament (5 ani)...")

# Perioada (1825 zile = 5 ani)
start_date = date(2019, 1, 1)
zile = 1825

date_list = [start_date + timedelta(days=x) for x in range(zile)]
luni = [d.month for d in date_list]
zile_an = [d.timetuple().tm_yday for d in date_list]

# 1. Generăm temperaturi (Curbă anuală: rece iarna, cald vara)

tavg = 12 + 14 * np.sin(2 * np.pi * (np.array(zile_an) - 105) / 365) + np.random.normal(0, 3, zile)
tmin = tavg - np.random.uniform(3, 7, zile)
tmax = tavg + np.random.uniform(3, 7, zile)

# 2. Generăm Presiune și Umiditate
# Umiditatea e mai mare iarna/toamna. Presiunea variază aleator.
humidity = np.clip(65 + 15 * np.cos(2 * np.pi * (np.array(zile_an)) / 365) + np.random.normal(0, 10, zile), 30, 100)
pressure = np.random.normal(1013, 8, zile)

# 3. Generăm Ploaia 
prcp = np.zeros(zile)
for i in range(zile):
    # REGULA:  furtună dacă umiditatea e mare (>75%) și presiunea e scăzută (<1010 hPa)
    if humidity[i] > 75 and pressure[i] < 1010:
        prcp[i] = np.random.exponential(scale=6) # Ploaie cantitativă
    elif humidity[i] > 85:
        prcp[i] = np.random.exponential(scale=2) # Burniță/Ploaie ușoară 
    else:
        # 10% șanse de ploaie aleatoare ușoară în restul zilelor
        if np.random.rand() > 0.9:
            prcp[i] = np.random.uniform(0.1, 2.0)

# 4. Rotunjim datele pentru a arăta exact ca senzorii reali
df = pd.DataFrame({
    'date': date_list,
    'month': luni,
    'tmin': np.round(tmin, 1),
    'tmax': np.round(tmax, 1),
    'tavg': np.round(tavg, 1),
    'humidity': np.round(humidity, 1),
    'pressure': np.round(pressure, 1),
    'prcp': np.round(prcp, 2)
})

# 5. Salvăm fișierul direct unde trebuie
df.to_csv("data/processed/weather_clean.csv", index=False)

print(f"🎉 GATA! Am generat și salvat cu succes {len(df)} rânduri în weather_clean.csv!")
print("Acum AI-ul tău are o bază de date uriașă și perfectă din care să învețe.")