import sys
import os
import pandas as pd

# Nota: El nombre del script ha cambiado de inferenciaVecinos.py a inferenciaNacional.py
CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]

# Definiciones de rutas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
TEMP_POLLUTION_DIR = os.path.join(BASE_DIR, "temp", "pollution")
NATIONAL_RATIOS_FILE = os.path.join(TEMP_POLLUTION_DIR, "national_ratios.csv")

# Función Auxiliar
def is_valid_number(x):
    try:
        return float(x) > 0
    except:
        return False

def main():
    if len(sys.argv) != 2:
        # El script sigue esperando la carpeta de la región como argumento
        print("Uso: inferenciaNacional.py <region_folder>")
        sys.exit(1)

    region_folder = sys.argv[1]
    region_name = os.path.basename(region_folder.rstrip("/"))

    ratios_csv = os.path.join(region_folder, f"{region_name}_ratios.csv")

    # 1. Verificamos si los archivos existen
    if not os.path.isfile(ratios_csv):
        print(f"ERROR: Archivo de Ratios no encontrado: {ratios_csv}")
        sys.exit(1)
    if not os.path.isfile(NATIONAL_RATIOS_FILE):
        print(f"ERROR: Archivo de Ratios Nacionales no encontrado: {NATIONAL_RATIOS_FILE}. Ejecute ratiosNacionales.py primero.")
        sys.exit(1)

    # 2. Cargamos ratios de la región
    try:
        df_ratios = pd.read_csv(ratios_csv, sep=';')
    except Exception as e:
        print(f"ERROR: No se puede leer el archivo de ratios regional: {e}")
        sys.exit(1)

    # 3. Cargamos los ratios nacionales
    try:
        # El 'id' se lee como índice (o como columna, dependiendo de cómo lo guardó pandas, 
        # pero como solo hay 1 fila, es fácil acceder)
        df_national = pd.read_csv(NATIONAL_RATIOS_FILE, sep=';', index_col=0)
        national_ratios = df_national.iloc[0].to_dict() # Convertimos la única fila a diccionario
    except Exception as e:
        print(f"ERROR: No se puede leer el archivo de ratios nacionales: {e}")
        sys.exit(1)

    # 4. Procesamos cada fila de la región
    for idx, row in df_ratios.iterrows():
        updated = False
        for pollutant in CONTAMINANTES:
            # Si el valor de la región es válido, lo saltamos
            if is_valid_number(row.get(pollutant, 0)):
                continue

            # Usamos el ratio nacional para este contaminante
            national_ratio = national_ratios.get(pollutant)

            if national_ratio is not None and is_valid_number(national_ratio):
                df_ratios.at[idx, pollutant] = national_ratio
                updated = True
                
        if updated:
            print(f"Actualizada fila con id={row['id']} con el promedio nacional.")

    # 5. Escribimos en el archivo de salida
    try:
        df_ratios.to_csv(ratios_csv, sep=';', index=False)
        print("ÉXITO")
        print(f"Ratios regionales actualizados guardados en: \n{ratios_csv}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar los ratios actualizados: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()