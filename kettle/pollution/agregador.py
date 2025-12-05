#!/usr/bin/env python3

import pandas as pd

# Paths
super_csv_path = "../../temp/pollution/super.csv"
total_csv_path = "../../dist/kettle/total_pollution.csv"

# Read super.csv
try:
    df = pd.read_csv(super_csv_path, sep=';')
except Exception as e:
    print(f"ERROR: Could not read {super_csv_path}: {e}")
    exit(1)

# Ensure numeric columns are floats
pollutants = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
for col in pollutants:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Group by date (year) and region, then calculate mean for pollutants
agg_df = df.groupby(['date', 'region'], as_index=False)[pollutants].mean()

# Sort by region and date for readability
agg_df = agg_df.sort_values(by=['region', 'date'])

# Save to total_polution.csv
try:
    agg_df.to_csv(total_csv_path, sep='\t', index=False)
    print(f"Aggregated total CSV saved to {total_csv_path}")
except Exception as e:
    print(f"ERROR: Could not save {total_csv_path}: {e}")
    exit(1)
