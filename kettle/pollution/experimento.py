import sys 
import pandas as pd 

EXPECTED_COLUMNS = [ 'date', ' pm25', ' pm10', ' o3', ' no2', ' so2', ' co']

def main():
    # Expect: region, file_path
    if len(sys.argv) !=3:
        print("Usage: same_format.py <region> <file.csv>")
        sys.exit(1)
        
    region = sys.argv[1]
    file_path = sys.argv[2]
    
    try:
        df = pd.read_csv(file_path)
        print("EXITO")
    except Exception as e:
        print(f"ERROR: Could not read {file_path}: {e}")
        sys.exit(1)
        
    # Check if all expectes columns re present
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    print(df.columns)
    if not missing:
        print(f"{file_path}: good")
    else:
        print(f"{file_path}: missing columns -> {missing}")
        
if __name__ == "__main__":
    main()
    print("THIS EXECUTED")