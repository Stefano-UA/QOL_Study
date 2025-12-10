import sys
import os
import pandas as pd
import numpy as np

# Constantes y Rutas
CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]
SUPER_CSV = "../../temp/pollution/super.csv"
RATIOS_CSV = "../../temp/pollution/ratios.csv"

# Columnas clave para el join y busqueda de ratios
KEY_COLUMNS = ['year', 'region', 'sensor']
FALLBACK_ID = 'ZZZZZZZZZZ'

def main():
    if len(sys.argv) != 1:
        print("Uso: inferencia.py (trabaja directamente con super.csv)")
        sys.exit(1)

    # PASO 1 - Cargamos los Datos
    if not os.path.isfile(SUPER_CSV) or not os.path.isfile(RATIOS_CSV):
        print("ERROR: Archivo SUPER_CSV o RATIOS_CSV no encontrado. Ejecuta las etapas previas.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(SUPER_CSV, sep=';')
        df_ratios = pd.read_csv(RATIOS_CSV, sep=';')
    except Exception as e:
        print(f"ERROR al leer archivos: {e}")
        sys.exit(1)

    # PASO 2 - Prepocesamiento
    all_pollutants = ['pm25'] + CONTAMINANTES
    for col in all_pollutants:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df.loc[df[col] < 0, col] = np.nan
    
    # Asegurar que las columnas por las que agregamos son estring
    for col in KEY_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str)
        if col in df_ratios.columns:
            df_ratios[col] = df_ratios[col].astype(str)
    
    # PASO 3 - Cargamos los Ratios
    
    # Aislamos la media nacional
    df_fallback_ratio = df_ratios[
        (df_ratios['year'] == FALLBACK_ID) & 
        (df_ratios['region'] == FALLBACK_ID) & 
        (df_ratios['sensor'] == FALLBACK_ID)
    ].drop(columns=KEY_COLUMNS).iloc[0] # Tomamos la primera (y única) fila
    
    # Nos quedamos con los otros
    df_ratios_specific = df_ratios[
        df_ratios['year'] != FALLBACK_ID
    ]
    
    # PASO 4 - Juntamos datos y ratios en un mismo DataFrame
    ratio_cols_map = {p: f'ratio_{p}' for p in CONTAMINANTES}
    df_ratios_specific = df_ratios_specific.rename(columns=ratio_cols_map)

    df = df.merge(
        df_ratios_specific[KEY_COLUMNS + list(ratio_cols_map.values())], 
        on=KEY_COLUMNS, 
        how='left'
    )
    
    # --- ETAPA A: INFERENCIA PM2.5 ---
    print("----ETAPA A: Inferencia Vectorizada de PM2.5----")
    
    # Máscara para filas que necesitan inferencia
    needs_pm25_inference = df['pm25'].isna() & df[CONTAMINANTES].notna().any(axis=1)

    # 1. Conseguir Inferencias
    inferred_pm25_cols = []
    
    for p in CONTAMINANTES:
        ratio_col = f'ratio_{p}'
        inferred_col = f'inferred_pm25_{p}'
        
        # A. Aplicar Fallback: Si el ratio específico es NaN (no hubo match), usar el ratio nacional
        df.loc[df[ratio_col].isna(), ratio_col] = df_fallback_ratio[p]

        # B. Calcular PM2.5 Inferido
        # Solo calculamos si el ratio > 0 y el contaminante [p] no es NaN
        df[inferred_col] = np.where(
            (df[ratio_col] > 0) & (df[p].notna()),
            df[p] * df[ratio_col],
            np.nan
        )
        inferred_pm25_cols.append(inferred_col)

    # 2. Aplicar la Media de las Inferencias de PM2.5
    mean_pm25_inferred = df[inferred_pm25_cols].mean(axis=1, skipna=True)
    
    df.loc[needs_pm25_inference, 'pm25'] = mean_pm25_inferred[needs_pm25_inference]

    # 3. Filtrar filas que no pudieron inferirse (si pm25 sigue siendo NaN)
    rows_before_filter = len(df)
    df = df.dropna(subset=['pm25'])
    print(f"  > Filas borradas por PM25 no válido/no inferible: {rows_before_filter - len(df)}")
    
    
    # --- ETAPA B: INFERENCIA OTROS CONTAMINANTES ---
    print("----ETAPA B: Inferencia Vectorizada de Otros Contaminantes----")
    
    for p in CONTAMINANTES:
        ratio_col = f'ratio_{p}'
        needs_inf = df[p].isna() # Máscara para filas donde el contaminante [p] está missing

        # 1. Calcular el valor inferido (PM25 / Ratio) para el subset
        inferred_value = df['pm25'] / df[ratio_col]
        
        # 2. Definir la condición de inferencia solo para las filas faltantes
        condition_to_infer = (df[ratio_col] > 0) & (df['pm25'].notna())
        
        # 3. Aplicar la asignación al subset:
        df.loc[needs_inf, p] = np.where(
            condition_to_infer.loc[needs_inf], 
            inferred_value.loc[needs_inf],     
            np.nan                             
        )

    # 8. Limpieza Final y Guardado
    
    # Columnas que deben conservarse (eliminando todas las auxiliares)
    COLUMNS_TO_KEEP = KEY_COLUMNS + all_pollutants
    
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