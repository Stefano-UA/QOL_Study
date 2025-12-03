import sys
import pandas as pd

EXPECTED_COLUMNS = ['date', 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co']

def limpiar_columas(col):
    return col.replace(" ", "")

def main():
    if len(sys.argv) != 2:
        print("Uso: formateadorLaMancha.py <file.csv>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Lo Leemos
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"ERROR: No se pudo leer {file_path}: {e}")
        sys.exit(1)

    # Limpiamos las columnas
    df.columns = [limpiar_columas(col) for col in df.columns]

    # Esquema SDS011 
    dic_cols = {
        "timestamp": "date",
        "P2": "pm25",  # PM2.5
        "P1": "pm10",  # PM10
    }

    # Creamos un nuevo DataFrame
    new_df = pd.DataFrame()

    for col in EXPECTED_COLUMNS:
        # Buscamos Columnas Orign
        cols_org = [src for src, dst in dic_cols.items() if dst == col]

        if len(cols_org) == 1 and cols_org[0] in df.columns:
            new_df[col] = df[cols_org[0]]
        else:
            new_df[col] = pd.NA

    # Formato de fecha YYYY/M/D
    if 'date' in new_df.columns:
        new_df['date'] = pd.to_datetime(new_df['date'], errors='coerce')
        new_df['date'] = new_df['date'].dt.strftime('%Y/%-m/%-d') 

    # Sobreescribir archivos.
    try:
        new_df.to_csv(file_path, sep=';', index=False)
    except Exception as e:
        print(f"ERROR: No se pudo sobreescribir el archivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
