import sys
import os
import pandas as pd
import numpy as np

# Constantes y Rutas
CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]
TEMP_POLLUTION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'pollution'))
SUPER_CSV = os.path.join(TEMP_POLLUTION_DIR, 'super.csv')
RATIOS_CSV = os.path.join(TEMP_POLLUTION_DIR, 'ratios.csv')

# Columnas clave para el join y busqueda de ratios
KEY_COLUMNS = ['year', 'region', 'sensor']
FALLBACK_ID = 'ZZZZZZZZZZ'

def main():
    # El script ahora trabaja con los archivos centrales, no necesita argumentos de región/archivo
    if len(sys.argv) != 1:
        print("Uso: inferencia.py (trabaja directamente con super.csv)")
        sys.exit(1)

    # 1. Carga de Datos
    if not os.path.isfile(SUPER_CSV) or not os.path.isfile(RATIOS_CSV):
        print("ERROR: Archivo SUPER_CSV o RATIOS_CSV no encontrado. Ejecuta las etapas previas.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(SUPER_CSV, sep=';')
        df_ratios = pd.read_csv(RATIOS_CSV, sep=';')
    except Exception as e:
        print(f"ERROR al leer archivos centrales: {e}")
        sys.exit(1)

    # 2. Pre-procesamiento y Limpieza (Vectorizado)
    
    # Aseguramos que los contaminantes sean numéricos (forzando no-numéricos a NaN)
    all_pollutants = ['pm25'] + CONTAMINANTES
    for col in all_pollutants:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Limpieza: Convertir valores < 0 a NaN
        df.loc[df[col] < 0, col] = np.nan
        
    # Asegurar que las columnas clave de ratios sean numéricas/string
    for col in CONTAMINANTES:
        df_ratios[col] = pd.to_numeric(df_ratios[col], errors='coerce')

    # Renombrar 'id' a 'sensor' en el DataFrame principal
    if 'id' in df.columns:
        df = df.rename(columns={'id': 'sensor'})
        
    # AÑADIDO: Asegurar que las claves de JOIN sean todas strings
    key_cols = ['year', 'region', 'sensor']

    for col in key_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
        if col in df_ratios.columns:
            df_ratios[col] = df_ratios[col].astype(str)
    
    # 3. Preparación de la Matriz de Ratios (Indexado para búsqueda rápida)
    
    # Separamos la fila de fallback
    df_fallback_ratio = df_ratios[
        (df_ratios['year'] == FALLBACK_ID) & 
        (df_ratios['region'] == FALLBACK_ID) & 
        (df_ratios['sensor'] == FALLBACK_ID)
    ].drop(columns=KEY_COLUMNS).iloc[0] # Tomamos la primera (y única) fila
    
    # El resto son los ratios específicos por (year, region, sensor)
    df_ratios_specific = df_ratios[
        df_ratios['year'] != FALLBACK_ID
    ].set_index(KEY_COLUMNS)
    
    
    # --- ETAPA A: INFERENCIA PM2.5 ---
    print("----ETAPA A: Inferencia Vectorizada de PM2.5----")
    
    # Máscara para filas que necesitan inferencia (pm25 es NaN, pero hay datos auxiliares)
    needs_pm25_inference = df['pm25'].isna() & df[CONTAMINANTES].notna().any(axis=1)

    # 4. Cálculo de Valores Inferidos de PM2.5 (para cada contaminante)
    inferred_pm25_cols = []
    
    for p in CONTAMINANTES:
        # A. Merge para obtener el ratio específico (si existe)
        # Hacemos un merge para traer la columna de ratios [p] para cada fila de df
        df = df.merge(
            df_ratios_specific[[p]].rename(columns={p: f'ratio_{p}'}), 
            on=KEY_COLUMNS, 
            how='left'
        )

        # B. Aplicar Fallback: Si el ratio específico es NaN, usar el ratio nacional
        ratio_col = f'ratio_{p}'
        df.loc[df[ratio_col].isna(), ratio_col] = df_fallback_ratio[p]

        # C. Calcular PM2.5 Inferido si el ratio es válido
        inferred_col = f'inferred_pm25_{p}'
        
        # Solo calculamos si el ratio > 0 y el contaminante [p] > 0
        df[inferred_col] = np.where(
            (df[ratio_col] > 0) & (df[p].notna()),
            df[p] * df[ratio_col],
            np.nan
        )
        inferred_pm25_cols.append(inferred_col)

    # 5. Aplicar la Media de las Inferencias de PM2.5
    # Calcular el promedio de todas las columnas inferidas (ignora NaNs)
    mean_pm25_inferred = df[inferred_pm25_cols].mean(axis=1, skipna=True)
    
    # Aplicar el valor de la media solo donde se necesite (needs_pm25_inference)
    df.loc[needs_pm25_inference, 'pm25'] = mean_pm25_inferred[needs_pm25_inference]

    # 6. Filtrar filas que no pudieron inferirse (si pm25 sigue siendo NaN)
    rows_before_filter = len(df)
    df = df.dropna(subset=['pm25'])
    print(f"  > Filas borradas por PM25 no válido/no inferible: {rows_before_filter - len(df)}")
    
    
    # --- ETAPA B: INFERENCIA OTROS CONTAMINANTES ---
    print("----ETAPA B: Inferencia Vectorizada de Otros Contaminantes----")
    
    for p in CONTAMINANTES:
    
        ratio_col = f'ratio_{p}'
        needs_inf = df[p].isna() # Mask for rows where pollutant [p] is missing

        # 1. Calculate the inferred value (full series, temporary)
        inferred_value = df['pm25'] / df[ratio_col]
        
        # 2. Define the inference condition only for the rows that are missing [p]
        # We check if the ratio > 0 AND PM25 is valid (which it should be)
        condition_to_infer = (df[ratio_col] > 0) & (df['pm25'].notna())
        
        # 3. Apply the final assignment to the subset of rows needing inference
        df.loc[needs_inf, p] = np.where(
            condition_to_infer.loc[needs_inf], # Condition filtered by the assignment mask
            inferred_value.loc[needs_inf],     # True value filtered by the assignment mask
            np.nan                             # False value (NaN for the subset)
        )

    # 4. Limpieza Final y Guardado
    
    # Columnas que deben conservarse
    COLUMNS_TO_KEEP = ['year', 'region', 'sensor'] + all_pollutants
    
    # Limpiar columnas auxiliares creadas
    df_final = df[COLUMNS_TO_KEEP].copy()
        
    try:
        df_final.to_csv(SUPER_CSV, sep=';', index=False)
        print("ÉXITO")
        print(f"Inferencia Completa. SUPER_CSV actualizado en: \n{SUPER_CSV}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar {SUPER_CSV}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()