import sys 
import pandas as pd
import numpy as np 

EXPECTED_COLUMNS = ['date', 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co']

def limpiar_columas(col):
    return col.replace(" ", "")

def main():
    if len(sys.argv) !=3:
        print("Uso: formateador.py <region> <file.csv>")
        sys.exit(1)
        
    file_path = sys.argv[2]
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"ERROR leyendo {file_path}: {e}")
        sys.exit(1)
        
    # Limpiamos los nombres de columnas - Paso 1
    cleaned_columns = [limpiar_columas(col) for col in df.columns]
    df.columns = cleaned_columns 
    
    # Añadimos las columnas que faltan - Paso 2
    for expected_col in EXPECTED_COLUMNS:
        if expected_col not in df.columns:
            pos_inser = EXPECTED_COLUMNS.index(expected_col)
            df.insert(pos_inser, expected_col, np.nan)
            print(f"AÑADIDA LA COLUMNA: {expected_col}")
    
    # Reordenamos las columnas - Paso 3
    df = df[EXPECTED_COLUMNS]
    
    # Guardamos los Resultados CON SEMICOLON - Paso 4
    try:
        df.to_csv(file_path, sep=';', index=False)
        print("ÉXITO")
    except Exception as e:
        print(f"ERROR al guardar con semicolon {file_path}: {e}")
        df.to_csv(file_path, index= False)
            
if __name__ == "__main__":
    main()