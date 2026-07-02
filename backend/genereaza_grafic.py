import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


df = pd.read_csv('data/processed/weather_clean.csv')


nume_ploaie = 'precipitation' if 'precipitation' in df.columns else df.columns[-1]


coloane = ['month', 'tavg', 'tmin', 'tmax', 'humidity', 'pressure', nume_ploaie]
df_subset = df[coloane]


df_subset = df_subset.rename(columns={nume_ploaie: 'precipitation'})


correlatie = df_subset.corr()


plt.figure(figsize=(10, 8))
sns.heatmap(correlatie, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Matricea de Corelatie a Datelor Meteorologice', fontsize=16)


plt.savefig('matrice_corelatie.png')
plt.show()