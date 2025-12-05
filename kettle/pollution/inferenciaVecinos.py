import sys
import os
import pandas as pd

CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]

def is_valid_number(x):
    """Check if x is a number greater than 0."""
    try:
        return float(x) > 0
    except:
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: inferenciaVecinos.py <region_folder>")
        sys.exit(1)

    region_folder = sys.argv[1]
    region_name = os.path.basename(region_folder.rstrip("/"))

    ratios_csv = os.path.join(region_folder, f"{region_name}_ratios.csv")
    vecinos_txt = os.path.join(region_folder, f"{region_name}_vecinos.txt")

    # Check files exist
    if not os.path.isfile(ratios_csv):
        print(f"ERROR: Ratios file not found: {ratios_csv}")
        sys.exit(1)
    if not os.path.isfile(vecinos_txt):
        print(f"ERROR: Neighbours file not found: {vecinos_txt}")
        sys.exit(1)

    # Load ratios
    try:
        df_ratios = pd.read_csv(ratios_csv, sep=';')
    except Exception as e:
        print(f"ERROR: Cannot read ratios CSV: {e}")
        sys.exit(1)

    if "id" not in df_ratios.columns:
        print(f"ERROR: Ratios CSV missing 'id' column")
        sys.exit(1)

    # Load neighbours
    with open(vecinos_txt, "r") as f:
        vecinos = [line.strip() for line in f if line.strip()]

    if not vecinos:
        print(f"ERROR: No neighbours listed in {vecinos_txt}")
        sys.exit(1)

    # Load neighbour ratios
    vecinos_dfs = {}
    for vecino in vecinos:
        vecino_csv = os.path.join("../../temp/pollution", vecino, f"{vecino}_ratios.csv")
        if os.path.isfile(vecino_csv):
            try:
                df = pd.read_csv(vecino_csv, sep=';')
                vecinos_dfs[vecino] = df
            except:
                pass  # skip invalid neighbour file

    if not vecinos_dfs:
        print("ERROR: No valid neighbour ratios found")
        sys.exit(1)

    # Process each row
    for idx, row in df_ratios.iterrows():
        updated = False
        for pollutant in CONTAMINANTES:
            if is_valid_number(row.get(pollutant, 0)):
                continue  # skip valid ratio

            # Gather valid neighbour ratios for this pollutant
            neighbour_values = []
            for vecino, vecino_df in vecinos_dfs.items():
                if pollutant in vecino_df.columns:
                    for val in vecino_df[pollutant]:
                        if is_valid_number(val):
                            neighbour_values.append(float(val))
            if neighbour_values:
                mean_ratio = sum(neighbour_values) / len(neighbour_values)
                df_ratios.at[idx, pollutant] = mean_ratio
                updated = True

        if updated:
            print(f"Updated row id={row['id']} with neighbour averages")

    # Overwrite CSV
    try:
        df_ratios.to_csv(ratios_csv, sep=';', index=False)
        print(f"Updated ratios saved to {ratios_csv}")
    except Exception as e:
        print(f"ERROR: Cannot save updated ratios CSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
