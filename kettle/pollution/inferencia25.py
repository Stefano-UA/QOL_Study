import sys
import os
import pandas as pd

CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]


# Funciones Auxiliares
def is_valid_number(x):
    """Return True if x is a number >= 0."""
    try:
        v = float(x)
        return v >= 0
    except:
        return False


def load_ratios(region, file_path):
    base_id = os.path.basename(file_path)[:10]
    ratio_csv = os.path.join("../../temp/pollution", region, f"{region}_ratios.csv")

    if not os.path.isfile(ratio_csv):
        print(f"ERROR: ARCHIVO RATIO NO ENCONTRADO: {ratio_csv}")
        sys.exit(1)

    df_rat = pd.read_csv(ratio_csv, sep=';')

    if "id" not in df_rat.columns:
        print("ERROR: EL ARCHIVO DE RATIOS NO TIENE COLUMNA 'ID'")
        sys.exit(1)

    match = df_rat[df_rat["id"].astype(str) == base_id]

    if match.empty:
        print(f"ERROR: RATIO NO ENCONTRADO PARA ID: {base_id} EN {ratio_csv}")
        sys.exit(1)

    return match.iloc[0] 


def main():
    if len(sys.argv) != 3:
        print("Uso: inferencia25.py <region> <file.csv>")
        sys.exit(1)

    region = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.isfile(file_path):
        print(f"ERROR: ARCHIVO NO ENCONTRADO: {file_path}")
        sys.exit(1)

    # Cargar ratios para el archivo espécifico
    ratios_row = load_ratios(region, file_path)

    # Leemos CSV
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"ERROR: NO SE PUEDE LEER {file_path} : {e}")
        sys.exit(1)

    # Nos aseguramos de que la columna exista
    for col in ["pm25"] + CONTAMINANTES:
        if col not in df.columns:
            df[col] = pd.NA

    new_rows = []
    previous_complete = None


    for idx, row in df.iterrows():
        row = row.copy()  # Copiamos por valor
        pm25_valid = is_valid_number(row["pm25"])

        pollutant_validity = {
            p: is_valid_number(row[p]) and float(row[p]) > 0
            for p in CONTAMINANTES
        }

        num_valid_pollutants = sum(pollutant_validity.values())

        # CASE A — BORRAMOS (nada valido)
        if (not pm25_valid) and num_valid_pollutants == 0:
            # No la ñadimos
            continue

        # CASE B — SALTAMOS (pm25 ya es valido)
        if pm25_valid:
            if all(is_valid_number(row[c]) for c in ["pm25"] + CONTAMINANTES):
                previous_complete = row.copy()
            new_rows.append(row)
            continue

        # CASE C — INFERENCIA (falta pm25)
        inferred_values = []

        for p in CONTAMINANTES:
            if not pollutant_validity[p]:
                continue

            ratio = ratios_row[p]

            if not is_valid_number(ratio) or float(ratio) == 0:
                continue

            inferred = float(row[p]) * float(ratio)
            inferred_values.append(inferred)

        if inferred_values:
            # Media de pm25 obtenidos
            row["pm25"] = sum(inferred_values) / len(inferred_values)
            new_rows.append(row)
            continue

        # CASE E — BORRAMOS (no se pude inferir)
        continue

    # Escribimos en archivo de salida
    out_file = file_path.replace(".csv", "_inferred.csv")
    out_df = pd.DataFrame(new_rows)
    out_df.to_csv(out_file, sep=';', index=False)

    print(f"Inferencia completada en: {out_file}")


if __name__ == "__main__":
    main()
