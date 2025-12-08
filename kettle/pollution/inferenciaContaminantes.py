import sys
import os
import pandas as pd

CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]


# Funciones Auxiliares
def is_valid_number(x):
    try:
        v = float(x)
        return v >= 0
    except:
        return False


def get_ratio_for_pollutant(df_ratios, file_id, pollutant):
    # Probamos nuestra fila
    match = df_ratios[df_ratios["id"].astype(str) == file_id]
    if not match.empty and is_valid_number(match.iloc[0][pollutant]) and float(match.iloc[0][pollutant]) > 0:
        return float(match.iloc[0][pollutant])

    # Sino probamos otra fila
    for idx, row in df_ratios.iterrows():
        if is_valid_number(row[pollutant]) and float(row[pollutant]) > 0:
            return float(row[pollutant])

    # Fracaso
    return None


def main():
    if len(sys.argv) != 3:
        print("Uso: inferenciaContaminantes.py <region> <file.csv>")
        sys.exit(1)

    region = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.isfile(file_path):
        print(f"ERROR: Archivo no encontrado: {file_path}")
        sys.exit(1)

    # Cargamos CSV
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"ERROR: No se puede leer {file_path} : {e}")
        sys.exit(1)

    # Chequeo columnas
    for col in ["pm25"] + CONTAMINANTES:
        if col not in df.columns:
            df[col] = pd.NA

    # Cargamos el CSV con los ratios
    ratio_csv = os.path.join("../../temp/pollution", region, f"{region}_ratios.csv")
    if not os.path.isfile(ratio_csv):
        print(f"ERROR: Archivo de Ratios no encotrado:  {ratio_csv}")
        sys.exit(1)

    try:
        df_ratios = pd.read_csv(ratio_csv, sep=';')
    except Exception as e:
        print(f"ERROR: No se puede leer el csv: {e}")
        sys.exit(1)

    if "id" not in df_ratios.columns:
        print(f"ERROR: Ratios CSV no tiene columa 'id': {ratio_csv}")
        sys.exit(1)

    file_id = os.path.basename(file_path)[:10]

    # Procesamos cada fila
    new_rows = []
    for idx, row in df.iterrows():
        row = row.copy()

        # Validez pm25
        if not is_valid_number(row["pm25"]):
            print(f"ERROR: Valor pm25 invalido en fila: {idx} de {file_path}")
            sys.exit(1)

        pm25_value = float(row["pm25"])

        # Procesamos cada contaminante
        for pollutant in CONTAMINANTES:
            if is_valid_number(row[pollutant]):
                continue 

            ratio = get_ratio_for_pollutant(df_ratios, file_id, pollutant)
            if ratio is None:
                print(f"ERROR: No se puede inferir {pollutant} para la fila {idx} en {file_path} por que no hay ratio valido")
                sys.exit(1)

            # Inferencia del Contaminante
            row[pollutant] = pm25_value / ratio

        new_rows.append(row)

    # Escribimos en Archivo de salida
    out_df = pd.DataFrame(new_rows)
    try:
        out_df.to_csv(file_path, sep=';', index=False)
        print("ÉXITO")
        print(f"Inferencia Completada, el CSV inferido es: \n{file_path}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar: {file_path} porque {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
