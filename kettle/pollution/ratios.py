import sys
import os
import pandas as pd

CONTAMINANTES = ['pm10', 'o3', 'no2', 'so2', 'co']

def main():
    if len(sys.argv) != 3:
        print("Uso: ratioMaker.py <region> <file.csv>")
        sys.exit(1)

    region = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.isfile(file_path):
        print(f"ERROR: Archivo no encontrado: {file_path}")
        sys.exit(1)

    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"ERROR: No se pudo leer {file_path}: {e}")
        sys.exit(1)

    # Asegurarse de que todas las columnas existan
    expected_cols = ['pm25'] + CONTAMINANTES
    for col in expected_cols:
        if col not in df.columns:
            df[col] = pd.NA

    # Calcular ratios
    ratios = {}
    for pol in CONTAMINANTES:
        valid_rows = df[['pm25', pol]].dropna()
        valid_rows = valid_rows.copy()
        valid_rows['pm25'] = pd.to_numeric(valid_rows['pm25'], errors='coerce')
        valid_rows[pol] = pd.to_numeric(valid_rows[pol], errors='coerce')
        valid_rows = valid_rows[(valid_rows['pm25'] > 0) & (valid_rows[pol] > 0)]

        if not valid_rows.empty:
            ratios[pol] = valid_rows['pm25'].mean() / valid_rows[pol].mean()
        else:
            ratios[pol] = 0

    # ID = primeros 10 caracteres del nombre del archivo
    id_row = os.path.basename(file_path)[:10]

    region_folder = os.path.join("../../temp/pollution", region)
    os.makedirs(region_folder, exist_ok=True)
    out_csv = os.path.join(region_folder, f"{region}_ratios.csv")

    # Crear o leer CSV de salida
    if os.path.isfile(out_csv):
        try:
            df_out = pd.read_csv(out_csv, sep=';')
        except Exception as e:
            print(f"ERROR: No se pudo leer {out_csv}: {e}")
            sys.exit(1)
    else:
        df_out = pd.DataFrame(columns=['id'] + CONTAMINANTES)

    # Asegurarse de que las columnas existan
    if 'id' not in df_out.columns:
        df_out['id'] = pd.Series(dtype=str)
    for pol in CONTAMINANTES:
        if pol not in df_out.columns:
            df_out[pol] = pd.NA

    # Saltar si ID ya existe
    if id_row in df_out['id'].astype(str).values:
        print(f"ID {id_row} ya existe en {out_csv}, saltando...")
        return

    # Agregar nueva fila
    new_row = {'id': id_row}
    new_row.update(ratios)
    df_out = pd.concat([df_out, pd.DataFrame([new_row])], ignore_index=True)

    try:
        df_out.to_csv(out_csv, sep=';', index=False)
        print("ÉXITO")
        print(f"Ratios guardados en \n”{out_csv}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar {out_csv}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
