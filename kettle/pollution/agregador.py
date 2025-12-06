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

# Lista de contaminantes
pollutants = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']

# Aseguramos valores numéricos
for col in pollutants:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# ----------------------------------------------------------
# PASO 1 — AGRUPAR POR AÑO Y REGIÓN Y CALCULAR MEDIAS
# ----------------------------------------------------------
agg_df = df.groupby(['date', 'region'], as_index=False)[pollutants].mean()


# ----------------------------------------------------------
# PASO 1b — AGREGAR "Nacional" COMO PROMEDIO DE TODAS LAS CCAA
# ----------------------------------------------------------
# Filtramos si quieres excluir "total_nacional" si ya existiera
agg_df_ccaa = agg_df[agg_df['region'] != 'total_nacional']

# Calculamos promedio por año
nacional_df = agg_df_ccaa.groupby('date', as_index=False)[pollutants].mean()
nacional_df['region'] = 'Nacional'  # O 'total_nacional', según convención

# Añadimos al dataframe original
agg_df = pd.concat([agg_df, nacional_df], ignore_index=True)

# ----------------------------------------------------------
# PASO 2 — CONVERTIR A FORMATO LARGO
# ----------------------------------------------------------
df_long = agg_df.melt(
    id_vars=["date", "region"],
    value_vars=pollutants,
    var_name="Type",
    value_name="Value"
)

# Quitar valores NaN
df_long = df_long.dropna(subset=["Value"])

# Renombrar columnas
df_long = df_long.rename(columns={
    "date": "Year",
    "region": "CCAA"
})

# Ordenar
df_long = df_long.sort_values(
    by=["Year", "CCAA", "Type"],
    ascending=[True, True, True]
)

# ----------------------------------------------------------
# PASO 3 — GUARDAR ARCHIVO FINAL
# ----------------------------------------------------------
try:
    df_long.to_csv(total_csv_path, sep='\t', index=False)
    print(f"Aggregated total CSV saved to {total_csv_path}")
except Exception as e:
    print(f"ERROR: Could not save {total_csv_path}: {e}")
    exit(1)
