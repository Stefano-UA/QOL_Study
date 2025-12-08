import pandas as pd
import os
import sys

# Definimos las rutas y contaminantes
CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
TEMP_POLLUTION_DIR = os.path.join(BASE_DIR, "temp", "pollution")
OUTPUT_FILE = os.path.join(TEMP_POLLUTION_DIR, "national_ratios.csv")

def is_valid_number(x):
    """Verifica si un valor es un número positivo válido."""
    try:
        return float(x) > 0
    except:
        return False

def calculate_national_ratios():
    """Calcula y guarda los ratios nacionales promedio."""
    all_ratios = []

    # Buscamos directorios de regiones dentro de temp/pollution
    region_folders = [d for d in os.listdir(TEMP_POLLUTION_DIR) 
                      if os.path.isdir(os.path.join(TEMP_POLLUTION_DIR, d))]

    if not region_folders:
        print(f"Advertencia: No se encontraron carpetas de regiones en {TEMP_POLLUTION_DIR}")
        return

    print(f"Encontradas {len(region_folders)} regiones.")

    # 1. Recoger todos los ratios de todas las regiones
    for region in region_folders:
        region_dir = os.path.join(TEMP_POLLUTION_DIR, region)
        ratios_csv = os.path.join(region_dir, f"{region}_ratios.csv")
        
        if os.path.isfile(ratios_csv):
            try:
                # Leemos sólo las columnas de ratios
                df = pd.read_csv(ratios_csv, sep=';', usecols=['id'] + CONTAMINANTES)
                
                # Filtramos y convertimos a valores numéricos válidos
                for col in CONTAMINANTES:
                    # Rellenamos no válidos (incluyendo NaN) con 0 para excluirlos del promedio
                    df[col] = df[col].apply(lambda x: float(x) if is_valid_number(x) else 0)
                
                # Excluimos filas que solo contienen 0s para el cálculo (aunque no debería pasar si se generó bien)
                # Al final solo necesitamos el DataFrame combinado para el cálculo
                all_ratios.append(df)
                
            except Exception as e:
                # Esto puede ocurrir si el archivo existe pero está vacío o mal formateado
                print(f"Advertencia: No se pudo leer ratios de {region}. Error: {e}")

    if not all_ratios:
        print("ERROR: No se encontraron datos de ratios válidos en ninguna región.")
        sys.exit(1)

    # 2. Combinar todos los DataFrames y calcular el promedio nacional
    combined_df = pd.concat(all_ratios, ignore_index=True)
    
    national_averages = {}
    
    for pollutant in CONTAMINANTES:
        # Filtramos los valores válidos (mayores a 0) antes de calcular el promedio
        valid_ratios = combined_df[combined_df[pollutant] > 0][pollutant]
        
        if not valid_ratios.empty:
            national_averages[pollutant] = valid_ratios.mean()
        else:
            print(f"Advertencia: No hay ratios válidos para {pollutant}. Se usará 1.0 como fallback.")
            national_averages[pollutant] = 1.0 # Valor de fallback

    # 3. Crear el DataFrame final con los promedios
    # La columna 'id' no es relevante para el promedio nacional, pero la usamos para el formato del CSV
    df_national = pd.DataFrame(national_averages, index=['National_Average'])
    df_national.index.name = 'id'
    
    # 4. Guardar el archivo de ratios nacionales
    try:
        # Asegurarse de que el directorio temporal existe
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df_national.to_csv(OUTPUT_FILE, sep=';', index=True)
        print("ÉXITO")
        print(f"Ratios nacionales guardados en: \n{OUTPUT_FILE}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el archivo de ratios nacionales: {e}")
        sys.exit(1)


if __name__ == "__main__":
    calculate_national_ratios()