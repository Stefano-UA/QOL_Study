import pandas as pd

# Rutas
super_csv_path = "../../temp/pollution/super.csv"
total_csv_path = "../../dist/kettle/total_pollution.csv"

# Leemos super.csv
try:
    df = pd.read_csv(super_csv_path, sep=';')
except Exception as e:
    print(f"ERROR: Could not read {super_csv_path}: {e}")
    exit(1)

# Nos aseguramos de que sean valores numéricos
pollutants = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
for col in pollutants:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Agrupando por región, año y sacando medias.
agg_df = df.groupby(['date', 'region'], as_index=False)[pollutants].mean()

# Ordenamos por región y año
agg_df = agg_df.sort_values(by=['region', 'date'])

# Guardamos total_polution.csv
try:
    agg_df.to_csv(total_csv_path, sep='\t', index=False)
    print(f"Aggregated total CSV saved to {total_csv_path}")
except Exception as e:
    print(f"ERROR: Could not save {total_csv_path}: {e}")
    exit(1)
