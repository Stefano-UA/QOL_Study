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

# ----------------------------------------------------------
# PASO 2 — CONVERTIR A FORMATO LARGO (WIDE → LONG)
# ----------------------------------------------------------
df_long = df_grouped.melt(
    id_vars=["date", "region"],
    value_vars=pollutants,
    var_name="Type",
    value_name="Value"
)

# Quitamos filas sin valor
df_long = df_long.dropna(subset=["Value"])

# Renombramos columnas
df_long = df_long.rename(columns={
    "date": "Year",
    "region": "CCAA"
})


# Ordenamos
df_long = df_long.sort_values(
    by=["Year", "CCAA", "Type"],
    ascending=[True, True, True]
)

# Guardamos total_polution.csv
try:
    agg_df.to_csv(total_csv_path, sep='\t', index=False)
    print(f"Aggregated total CSV saved to {total_csv_path}")
except Exception as e:
    print(f"ERROR: Could not save {total_csv_path}: {e}")
    exit(1)
