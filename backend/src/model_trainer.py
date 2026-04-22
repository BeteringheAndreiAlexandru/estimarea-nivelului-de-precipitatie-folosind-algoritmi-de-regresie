import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

def train_regression_model(data_path):
    """
    Antrenează un model de tip Random Forest.
    Se adaptează automat la coloanele disponibile în setul de date.
    """
    print(f"  -> Se încarcă datele pentru antrenare din {data_path}")
    df = pd.read_csv(data_path)

    # AICI ESTE REPARAȚIA: Afișăm exact ce coloane avem
    print(f"  -> Coloanele găsite în fișierul tău sunt: {list(df.columns)}")

    # 1. Selectarea variabilelor (Features). Aceasta este "lista de dorințe":
    features_ideale = ['month', 'tavg', 'tmin', 'tmax']
    
    # Filtrăm inteligent: Păstrăm DOAR coloanele care există cu adevărat în fișier
    features = [col for col in features_ideale if col in df.columns]
    target = 'prcp'

    if target not in df.columns:
        print(f"EROARE: Nu există coloana '{target}' (precipitații) în date!")
        return None, None

    print(f"  -> Modelul va învăța folosind DOAR aceste coloane valide: {features}")

    # Eliminăm rândurile care au lipsuri stricte (doar pe coloanele folosite)
    df = df.dropna(subset=features + [target])

    X = df[features]
    y = df[target]

    # 2. Împărțirea datelor (80% antrenare, 20% testare)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Antrenarea modelului
    print("  -> Se antrenează modelul Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 4. Generarea de predicții
    predictions = model.predict(X_test)
    predictions = np.maximum(predictions, 0) # Tăiem valorile negative

    # 5. Evaluarea performanței
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    metrics = {
        'MAE': round(mae, 2),
        'RMSE': round(rmse, 2)
    }

    print("\n  📊 Exemplu: Predicție vs. Realitate (primele 5 zile testate):")
    rezultate = pd.DataFrame({  
        'Real (mm)': y_test.values[:5], 
        'Prezis (mm)': np.round(predictions[:5], 1)
    })
    print(rezultate.to_string(index=False))

    # --- 6. VIZUALIZAREA REZULTATELOR ---
    print("\n  -> Se generează graficul rezultatelor. Închide fereastra graficului pentru a finaliza programul.")
    
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, predictions, alpha=0.5, color='blue', label='Zile Testate')
    
    max_val = max(y_test.max(), predictions.max()) if len(y_test) > 0 else 100
    plt.plot([0, max_val], [0, max_val], color='red', linestyle='--', linewidth=2, label='Predicție Perfectă')
    
    plt.title('Modelul Random Forest: Precipitații Reale vs. Prezise')
    plt.xlabel('Precipitații Reale (mm)')
    plt.ylabel('Precipitații Prezise de Model (mm)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

    return model, metrics