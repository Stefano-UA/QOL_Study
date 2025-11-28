# Estructura que Queremos
# date, pm25, pm10, o3, no2, so2, co

import os 
import glob 
import pandas as pd

EXPECTED_COLUMNS = ['date', 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co']

def check_csv_columns(csv_file):
    try:
        df = pd.read_csv(csv_file)

        if list(df.columns) != EXPECTED_COLUMNS:
            print(f"MEC MEC MEC: Could not read file {csv_file}.")
            return False
        else: 
            return True
    except Exception as e:
        print(f"ERROR: Could not read file {csv_file}. Exception: {str(e)}")

def check_csv_files(data_dir):
    if not os.path.exists(data_dir):
        print(f"The directory {data_dir} does not exist.")
        return 
    
    csv_count = 0
    contador_buenos = 0
    contador_malos = 0
    
    region_folders = glob.glob(os.path.join(data_dir, '*'))

    for region in region_folders:
        if os.path.isdir(region):
            print(f"Checking the files in {region}")
            csv_files = glob.glob(os.path.join(region, '*.csv'))

            if not csv_files:
                print(f"No CSV files found in {region}")
            else:
                csv_count += len(csv_files)
                for csv_file in csv_files:
                    if check_csv_columns(csv_file):
                        contador_buenos +=1
                    else:
                        contador_malos += 1
                    #print(f"Found CSV file: {csv_file}")
        else:
            print(f"Skipping {region}, not a directory.")
    
    print(f"\nFound: {csv_count}, Buenos: {contador_buenos}, Malos: {contador_malos}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    root_path = os.path.join(script_dir, '../../data/pollution') 
    check_csv_files(root_path)