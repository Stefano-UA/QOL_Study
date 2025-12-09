import sys
import os
import pandas as pd
import numpy as np

CONTAMINANTES = ['pm10', 'o3', 'no2', 'so2', 'co']

SUPER_CSV = os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'pollution', 'super.csv')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'pollution', 'ratios.csv')

# Columnas clave para identificar cada ratio de sensor
KEY_COLUMNS = ['year', 'region', 'sensor']

def calculate_ratios(df_group):
    """Calcula los ratios PM25/Contaminante para un DataFrame (grupo o nacional)."""
    
    df_group = df_group.copy()
    
    # 1. Asegurar tipos numéricos
    for col in ['pm25'] + CONTAMINANTES:
        df_group[col] = pd.to_numeric(df_group[col], errors='coerce')
    
    # 2. Filtrar por valores positivos de PM25
    df_valid = df_group[(df_group['pm25'] > 0)]
    
    ratios = {}
    for pol in CONTAMINANTES:
        
        # Filtrar para asegurar que el contaminante también es positivo
        df_pol_valid = df_valid[(df_valid[pol] > 0)].dropna(subset=['pm25', pol])

        if not df_pol_valid.empty:
            # Cálculo del ratio: (Mean PM25) / (Mean Pollutant)
            ratio = df_pol_valid['pm25'].mean() / df_pol_valid[pol].mean()
            ratios[pol] = ratio
        else:
            ratios[pol] = np.nan 

    return pd.Series(ratios)


def main():
    
    # 1. Cargar SUPER_CSV
    if not os.path.isfile(SUPER_CSV):
        print(f"ERROR: Archivo SUPER_CSV no encontrado: {SUPER_CSV}")
        sys.exit(1)

    try:
        df_super = pd.read_csv(SUPER_CSV, sep=';')
    except Exception as e:
        print(f"ERROR: No se pudo leer {SUPER_CSV} : {e}")
        sys.exit(1)
        
    # El archivo SUPER_CSV ahora debe tener 'year', 'region' y 'id' (que renombramos a 'sensor')
    # Renombramos 'id' a 'sensor' temporalmente para consistencia con el código
    if 'id' in df_super.columns:
        df_super = df_super.rename(columns={'id': 'sensor'})
    
    # 2. CALCULAR RATIOS POR GRUPO (YEAR, REGION, SENSOR)
    print("Calculando ratios por grupo (YEAR, REGION, SENSOR)...")
    
    # Agrupar y aplicar la función de cálculo
    df_ratios_grouped = df_super.groupby(KEY_COLUMNS).apply(calculate_ratios)
    
    # Limpiar el resultado: convertimos el índice multi-nivel en columnas
    df_ratios_grouped = df_ratios_grouped.reset_index()

    # 3. CALCULAR RATIOS NACIONALES (Fallback ZZZZZZZZZZ)
    print("Calculando ratio nacional (ZZZZZZZZZZ)...")
    df_ratios_national = calculate_ratios(df_super)
    
    # Crear la fila de fallback usando ZZZZZZZZZZ en las tres claves
    national_row = df_ratios_national.to_dict()
    national_row['year'] = 'ZZZZZZZZZZ'
    national_row['region'] = 'ZZZZZZZZZZ'
    national_row['sensor'] = 'ZZZZZZZZZZ'
    
    # 4. COMBINAR Y GUARDAR
    
    # Convertir la fila nacional en un DataFrame y luego combinar
    df_national_row = pd.DataFrame([national_row])
    
    # Aseguramos que todas las columnas de salida sean correctas
    FINAL_COLUMNS = KEY_COLUMNS + CONTAMINANTES
    
    df_final = pd.concat([df_ratios_grouped, df_national_row], ignore_index=True)
    df_final = df_final[FINAL_COLUMNS] # Reordenamos y aseguramos la estructura

    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df_final.to_csv(OUTPUT_FILE, sep=';', index=False)
        print("ÉXITO")
        print(f"Ratios guardados en \n{OUTPUT_FILE}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar {OUTPUT_FILE}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()