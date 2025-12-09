import sys 
import pandas as pd
import numpy as np 
import os

# Las columnas esperadas ahora NO deben tener espacios para la verificación/limpieza posterior
EXPECTED_COLUMNS = ['date', 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co']

def limpiar_columas(col):
    """Limpia espacios en los nombres de las columnas."""
    # Usamos strip() para limpiar espacios al inicio/fin, y replace(" ", "") por si hay internos
    return col.strip().replace(" ", "")

def main():
    if len(sys.argv) != 3:
        print("Uso: formateador.py <region> <file.csv>")
        sys.exit(1)
        
    region = sys.argv[1] # Aunque no se usa directamente en este script, se mantiene por el formato de llamada
    file_path = sys.argv[2]
    
    # 1. Lectura del CSV
    try:
        # Intentamos leer el archivo. Si el separador es variable (',' o ';'), Pandas lo detecta
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"ERROR leyendo {file_path}: {e}")
        sys.exit(1)
        
    # 2. Limpieza de nombres de columnas y Verificación Inicial (Fusión con cribadoInicial.py)
    
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
        
    # 3. Formateo y Estructuración (formateador.py)
    
    # Añadimos las columnas que faltan (Paso 2)
    for expected_col in EXPECTED_COLUMNS:
        if expected_col not in df.columns:
            # Encontrar posición para mantener orden (si es posible)
            try:
                pos_inser = EXPECTED_COLUMNS.index(expected_col)
                df.insert(pos_inser, expected_col, np.nan)
                print(f"AÑADIDA Y RELLENADA COLUMNA: {expected_col}")
            except Exception:
                # Si falla el insert, simplemente la añadimos al final.
                df[expected_col] = np.nan
    
    # Reordenamos las columnas (Paso 3)
    df = df[EXPECTED_COLUMNS]
    
    # 4. Guardamos los Resultados CON SEMICOLON (Paso 4)
    # Se sobrescribe el archivo original ya limpio
    try:
        df.to_csv(file_path, sep=';', index=False)
        print("----Formateo Completo----")
        print(f"ÉXITO, archivo guardado con ';' en: \n{file_path}")
    except Exception as e:
        print(f"ERROR al guardar con semicolon {file_path}: {e}")
        # Intento de guardar con formato por defecto si el semicolon falla
        df.to_csv(file_path, index= False)
        sys.exit(1) # Salimos si falla la escritura final
            
if __name__ == "__main__":
    main()