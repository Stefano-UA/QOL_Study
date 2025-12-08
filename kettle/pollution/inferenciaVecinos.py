import sys
import os
import pandas as pd

CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]

# Función Auxiliar
def is_valid_number(x):
    try:
        return float(x) > 0
    except:
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: inferenciaVecinos.py <region_folder>")
        sys.exit(1)

    region_folder = sys.argv[1]
    region_name = os.path.basename(region_folder.rstrip("/"))

    ratios_csv = os.path.join(region_folder, f"{region_name}_ratios.csv")
    vecinos_txt = os.path.join(os.path.dirname(__file__),"vecinos.txt")

    # Vemos si el archivo existe
    if not os.path.isfile(ratios_csv):
        print(f"ERROR: Archivo de Ratios no encontrado: {ratios_csv}")
        sys.exit(1)
    if not os.path.isfile(vecinos_txt):
        print(f"ERROR: Archivo del Veino no encontrado: {vecinos_txt}")
        sys.exit(1)

    # Cargamos ratios
    try:
        df_ratios = pd.read_csv(ratios_csv, sep=';')
    except Exception as e:
        print(f"ERROR: No se puede leer el archivo de ratios: {e}")
        sys.exit(1)

    if "id" not in df_ratios.columns:
        print(f"ERROR: CSV de Ratios no tiene columna 'id'")
        sys.exit(1)

    # Cargamos vecinos
    with open(vecinos_txt, "r") as f:
        vecinos = [line.strip() for line in f if line.strip()]

    if not vecinos:
        print(f"ERROR: No hay vecinos en: {vecinos_txt}")
        sys.exit(1)

    # Cargamos los ratios de los vecinos
    vecinos_dfs = {}
    for vecino in vecinos:
        vecino_csv = os.path.join("../../temp/pollution", vecino, f"{vecino}_ratios.csv")
        if os.path.isfile(vecino_csv):
            try:
                df = pd.read_csv(vecino_csv, sep=';')
                vecinos_dfs[vecino] = df
            except:
                pass  # Saltamos si es inválido

    if not vecinos_dfs:
        print("ERROR: Los vecinos no tiene ratios validos")
        sys.exit(1)

    # Procesamos cada fila
    for idx, row in df_ratios.iterrows():
        updated = False
        for pollutant in CONTAMINANTES:
            if is_valid_number(row.get(pollutant, 0)):
                continue  # nos saltamos validos

            # Usamos ratios de los vecinos para este contaminante
            neighbour_values = []
            for vecino, vecino_df in vecinos_dfs.items():
                if pollutant in vecino_df.columns:
                    for val in vecino_df[pollutant]:
                        if is_valid_number(val):
                            neighbour_values.append(float(val))
            if neighbour_values:
                mean_ratio = sum(neighbour_values) / len(neighbour_values)
                df_ratios.at[idx, pollutant] = mean_ratio
                updated = True

        if updated:
            print(f"Actualizada fila con id={row['id']} con los vecinos")

    # Escribimos en el archivo de salida
    try:
        df_ratios.to_csv(ratios_csv, sep=';', index=False)
        print("ÉXITO")
        print(f"Ratios actualizados guardados en: \n{ratios_csv}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar los ratios actualizados: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
