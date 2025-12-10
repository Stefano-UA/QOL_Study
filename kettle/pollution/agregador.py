import pandas as pd

# Constantes y Rutas
CONTAMINANTES = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
SUPER_CSV = "../../temp/pollution/super.csv"
OUTPUT_CSV = "../../dist/kettle/pollution.csv"

# Leemos super.csv
try:
    df = pd.read_csv(SUPER_CSV, sep=';')
except Exception as e:
    print(f"ERROR: Could not read {SUPER_CSV}: {e}")
    exit(1)



# Aseguramos valores numéricos
for col in CONTAMINANTES:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Borramos la columna sensor:
df = df.drop(columns=['sensor'])

# Paso 1 - Agregar y Sacar Medias
agg_df = df.groupby(['year', 'region'], as_index=False)[CONTAMINANTES].mean()


# PASO 1.5 - Agregamos a nivel nacional
# Calculamos promedio por año
nacional_df = agg_df.groupby('year', as_index=False)[CONTAMINANTES].mean()
nacional_df['region'] = 'total_nacional'  

# Añadimos al dataframe original
agg_df = pd.concat([agg_df, nacional_df], ignore_index=True)

# PASO 2 - Convertimos a Formato Largo
df_long = agg_df.melt(
    id_vars=["year", "region"],
    value_vars=CONTAMINANTES,
    var_name="Type",
    value_name="Value"
)

# Quitar valores NaN
df_long = df_long.dropna(subset=["Value"])

# Renombrar columnas
df_long = df_long.rename(columns={
    "year": "Year",
    "region": "CCAA"
})

# Ordenar
df_long = df_long.sort_values(
    by=["Year", "CCAA", "Type"],
    ascending=[True, True, True]
)

# PASO 3 - Guardamos
try:
    df_long.to_csv(OUTPUT_CSV, sep='\t', index=False)
    print("ÉXITO")
    print(f"Agregado el csv en: \n {OUTPUT_CSV}")
except Exception as e:
    print(f"ERROR: No se pudo guardar {OUTPUT_CSV}: {e}")
    exit(1)
