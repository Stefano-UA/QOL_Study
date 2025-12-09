import sys
import pandas as pd
import numpy as np # Necesario para pd.NA/np.nan
import os

# Columnas finales esperadas
EXPECTED_COLUMNS = ['date', 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co']

# Mapeo de columnas fuente del sensor SDS011 a las columnas finales
MAPPING_DICT = {
    "timestamp": "date",
    "P2": "pm25",  # PM2.5
    "P1": "pm10",  # PM10
}

# Columnas fuente que *deberían* estar en el archivo de Castilla-La Mancha
SOURCE_COLUMNS = list(MAPPING_DICT.keys())

def limpiar_columas(col):
    """Limpia espacios al inicio/fin en los nombres de las columnas."""
    return col.strip().replace(" ", "")

def main():
    if len(sys.argv) != 2:
        print("Uso: formateadorLaMancha.py <file.csv>")
        sys.exit(1)

    file_path = sys.argv[1]

    # 1. Lectura del CSV
    try:
        # Intentamos leer el archivo con el separador que ya usamos (;)
        # Si el archivo original fue formateado previamente, estará en ';'
        # Si es el archivo de entrada original, Pandas intentará inferir
        df = pd.read_csv(file_path, sep=';', dtype=str) # Leer como string para asegurar la limpieza
    except Exception as e:
        print(f"ERROR: No se pudo leer {file_path}: {e}")
        sys.exit(1)

    # 2. Limpieza de columnas y Cribado Inicial
    
    # Aplicamos la limpieza
    df.columns = [limpiar_columas(col) for col in df.columns]
    
    # Verificamos si las columnas fuente clave están presentes
    missing_source = [col for col in SOURCE_COLUMNS if col not in df.columns]
    
    if missing_source:
        print("----Cribado Inicial (ADVERTENCIA)----")
        print(f"Columnas fuente necesarias: {SOURCE_COLUMNS}")
        print(f"FALTAN COLUMNAS FUENTE CLAVE -> {missing_source} en: \n{file_path}")
        # NOTA: No hacemos sys.exit(1) para intentar procesar lo que haya.

    # 3. Formateo y Mapeo de Datos

    new_df = pd.DataFrame()

    for col_final in EXPECTED_COLUMNS:
        # Buscamos la columna fuente mapeada
        col_source = MAPPING_DICT.get(col_final)
        
        if col_source and col_source in df.columns:
            # Si encontramos la columna fuente, la copiamos
            new_df[col_final] = df[col_source]
        else:
            # Si no hay mapeo o la columna fuente no existe, rellenamos con NaN
            new_df[col_final] = np.nan 

    # 4. Formato de fecha YYYY/M/D (Aplica solo a la columna 'date' si existe)
    if 'date' in new_df.columns:
        # Aseguramos que los valores sean strings antes de la conversión
        new_df['date'] = new_df['date'].astype(str)
        new_df['date'] = pd.to_datetime(new_df['date'], errors='coerce', utc=True)
        
        # Formato de salida: YYYY/M/D (sin cero inicial en M y D)
        # Usamos .dt.strftime('%Y/%#m/%#d') para Python/Linux, o '%Y/%-m/%-d' para otros
        # Para máxima compatibilidad, usaremos la notación que limpia ceros:
        new_df['date'] = new_df['date'].dt.strftime('%Y/%m/%d').str.replace('/0', '/')
        new_df['date'] = new_df['date'].str.replace('/0', '/', regex=False) # Eliminamos el 0 en M y D

    # 5. Sobreescribir archivos con ';'
    try:
        new_df.to_csv(file_path, sep=';', index=False)
        print("----Formato Castilla-La Mancha Completo----")
        print("ÉXITO")
    except Exception as e:
        print(f"ERROR: No se pudo sobreescribir el archivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()