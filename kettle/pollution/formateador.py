import sys 
import pandas as pd
import numpy as np 

# Constante
EXPECTED_COLUMNS = ['date', 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co']

def limpiar_columas(col):
    """Limpia espacios en los nombres de las columnas."""
    # Usamos strip() para limpiar espacios al inicio/fin, y replace(" ", "") por si hay internos
    return col.strip().replace(" ", "")

def main():
    if len(sys.argv) != 2:
        print("Uso: formateador.py <region> <file.csv>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    # PASO 1 - Lectura del CSV
    try:
        # Intentamos leer el archivo
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"ERROR leyendo {file_path}: {e}")
        sys.exit(1)
        
    # PASO 2 - Cribado y Limpeiza de Columnas
    
    # Aplicamos la limpieza a todos los nombres de columnas
    cleaned_columns = [limpiar_columas(col) for col in df.columns]
    df.columns = cleaned_columns 
    
    # Verificamos qué columnas faltan después de la limpieza
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    
    if missing:
        # Este es el "Cribado Inicial" - Advertimos sobre las columnas faltantes
        print("----Cribado Inicial (ADVERTENCIA)----")
        print(f"Columnas después de la limpieza: {list(df.columns)}")
        print(f"FALTAN COLUMNAS CLAVE -> {missing} en: \n{file_path}")
        # NOTA: No hacemos sys.exit(1) aquí, ya que el formateador las añadirá con NaN.
        
    # PASO 3 - Formateo y Estructuración 
    
    # Añadimos las columnas que faltan
    for expected_col in EXPECTED_COLUMNS:
        if expected_col not in df.columns:
            try:
                pos_inser = EXPECTED_COLUMNS.index(expected_col)
                df.insert(pos_inser, expected_col, np.nan)
                print(f"AÑADIDA Y RELLENADA COLUMNA: {expected_col}")
            except Exception:
                df[expected_col] = np.nan
    
    # Reordenamos las columnas 
    df = df[EXPECTED_COLUMNS]
    
    # PASO 4 - Guardamos los Resultados (;)
    # Se sobrescribe el archivo original ya limpio
    try:
        df.to_csv(file_path, sep=';', index=False)
        print("----Formateo Completo----")
        print(f"ÉXITO, archivo guardado con ';' en: \n{file_path}")
    except Exception as e:
        print(f"ERROR al guardar con semicolon {file_path}: {e}")
        df.to_csv(file_path, index= False)
        sys.exit(1) 
            
if __name__ == "__main__":
    main()