import os
import pandas as pd
import glob

# Get the current directory
current_directory = os.getcwd()
print(current_directory)

# Find all CSV files in the current directory
csv_files = glob.glob(os.path.join(current_directory, '*.csv'))
print(csv_files)

# Loop through each file and print its column names
for csv_file in csv_files:
    try:
        # Attempt to read the CSV file, handle different delimiters and encoding
        df = pd.read_csv(csv_file, delimiter=None, encoding='utf-8')  # Let pandas auto-detect delimiter
        print(f"{csv_file}: {list(df.columns)}")
    except Exception as e:
        print(f"Could not read file {csv_file}: {str(e)}")


