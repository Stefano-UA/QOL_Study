import sys
import os
import pandas as pd

CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]


# -----------------------------
# Helper functions
# -----------------------------
def is_valid_number(x):
    """Return True if x is a number >= 0."""
    try:
        v = float(x)
        return v >= 0
    except:
        return False


def get_ratio_for_pollutant(df_ratios, file_id, pollutant):
    """Get ratio for the given pollutant and file ID.
    If not found for this ID, try any other row in the CSV.
    """
    # First try the exact file ID
    match = df_ratios[df_ratios["id"].astype(str) == file_id]
    if not match.empty and is_valid_number(match.iloc[0][pollutant]) and float(match.iloc[0][pollutant]) > 0:
        return float(match.iloc[0][pollutant])

    # Try any other row
    for idx, row in df_ratios.iterrows():
        if is_valid_number(row[pollutant]) and float(row[pollutant]) > 0:
            return float(row[pollutant])

    # Not found anywhere
    return None


# -----------------------------
# Main processing
# -----------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: inferenciaContaminantes.py <region> <file.csv>")
        sys.exit(1)

    region = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.isfile(file_path):
        print(f"ERROR: File not found → {file_path}")
        sys.exit(1)

    # Load CSV
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"ERROR: Cannot read {file_path} → {e}")
        sys.exit(1)

    # Ensure necessary columns exist
    for col in ["pm25"] + CONTAMINANTES:
        if col not in df.columns:
            df[col] = pd.NA

    # Load ratios CSV
    ratio_csv = os.path.join("../../data/pollution", region, f"{region}_ratios.csv")
    if not os.path.isfile(ratio_csv):
        print(f"ERROR: Ratios file not found → {ratio_csv}")
        sys.exit(1)

    try:
        df_ratios = pd.read_csv(ratio_csv, sep=';')
    except Exception as e:
        print(f"ERROR: Cannot read ratios CSV → {e}")
        sys.exit(1)

    if "id" not in df_ratios.columns:
        print(f"ERROR: Ratios CSV missing 'id' column → {ratio_csv}")
        sys.exit(1)

    file_id = os.path.basename(file_path)[:10]

    # Process each row
    new_rows = []
    for idx, row in df.iterrows():
        row = row.copy()

        # Check pm25 validity
        if not is_valid_number(row["pm25"]):
            print(f"ERROR: pm25 missing or invalid in row {idx} of {file_path}")
            sys.exit(1)

        pm25_value = float(row["pm25"])

        # Process each pollutant
        for pollutant in CONTAMINANTES:
            if is_valid_number(row[pollutant]):
                continue  # leave valid values

            ratio = get_ratio_for_pollutant(df_ratios, file_id, pollutant)
            if ratio is None:
                print(f"ERROR: Cannot infer {pollutant} for row {idx} in {file_path} → no valid ratio found")
                sys.exit(1)

            # Infer pollutant
            row[pollutant] = pm25_value / ratio

        new_rows.append(row)

    # Overwrite CSV
    out_df = pd.DataFrame(new_rows)
    try:
        out_df.to_csv(file_path, sep=';', index=False)
        print(f"Inference complete, CSV overwritten → {file_path}")
    except Exception as e:
        print(f"ERROR: Cannot save {file_path} → {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
