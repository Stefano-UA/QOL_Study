import sys 
import pandas as pd 

EXPECTED_COLUMNS = [ 'date', ' pm25', ' pm10', ' o3', ' no2', ' so2', ' co']

def main():
    # Comprobamos los argumentos
    if len(sys.argv) !=3:
        print("Uso: same_format.py <region> <file.csv>")
        sys.exit(1)
        
    file_path = sys.argv[2]
    
    # Probamos a leer
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"ERROR: No se pudo leer {file_path}: {e}")
        sys.exit(1)
        
    # Ver que columnas faltan
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    print(f"Las columnas DEBERIAN ser: {[columna for columna in df.columns]}")
    if not missing:
        print(f"TODO CORRECTO en: \n{file_path}")
    else:
        print(f"Y FALTAN -> {missing} en: \n{file_path}")
        
if __name__ == "__main__":
    main()
