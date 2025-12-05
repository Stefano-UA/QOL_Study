import sys
import os
import pandas as pd

CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]


# -----------------------------
# Helpers
# -----------------------------
def is_valid_number(x):
    """Return True if x is a number >= 0."""
    try:
        v = float(x)
        return v >= 0
    except:
        return False


def load_ratios(region, file_path):
    """Load the ratio row for the given file (first 10 chars as ID)."""
    base_id = os.path.basename(file_path)[:10]
    ratio_csv = os.path.join("../../temp/pollution", region, f"{region}_ratios.csv")

    if not os.path.isfile(ratio_csv):
        print(f"ERROR: RATIOS FILE NOT FOUND → {ratio_csv}")
        sys.exit(1)

    df_rat = pd.read_csv(ratio_csv, sep=';')

    if "id" not in df_rat.columns:
        print("ERROR: RATIOS FILE HAS NO 'id' COLUMN")
        sys.exit(1)

    match = df_rat[df_rat["id"].astype(str) == base_id]

    if match.empty:
        print(f"ERROR: NO RATIO FOUND FOR ID {base_id} IN {ratio_csv}")
        sys.exit(1)

    return match.iloc[0]  # row


# -----------------------------
# Main Inference Procedure
# -----------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: inferencia25.py <region> <file.csv>")
        sys.exit(1)

    region = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.isfile(file_path):
        print(f"ERROR: FILE NOT FOUND → {file_path}")
        sys.exit(1)

    # Load ratios for the specific file
    ratios_row = load_ratios(region, file_path)

    # Read CSV
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"ERROR: CANNOT READ {file_path} → {e}")
        sys.exit(1)

    # Ensure necessary columns exist
    for col in ["pm25"] + CONTAMINANTES:
        if col not in df.columns:
            df[col] = pd.NA

    new_rows = []
    previous_complete = None

    # -----------------------------------
    # Iterate through all rows
    # -----------------------------------
    for idx, row in df.iterrows():
        row = row.copy()  # Safety to avoid chained assignment traps
        pm25_valid = is_valid_number(row["pm25"])

        pollutant_validity = {
            p: is_valid_number(row[p]) and float(row[p]) > 0
            for p in CONTAMINANTES
        }

        num_valid_pollutants = sum(pollutant_validity.values())

        # CASE A — Delete row (no valid pm25 AND no valid pollutant)
        if (not pm25_valid) and num_valid_pollutants == 0:
            # silently remove
            continue

        # CASE B — pm25 already OK → just keep it
        if pm25_valid:
            # Check if it's a COMPLETE row
            if all(is_valid_number(row[c]) for c in ["pm25"] + CONTAMINANTES):
                previous_complete = row.copy()
            new_rows.append(row)
            continue

        # CASE C — pm25 missing but we can infer
        inferred_values = []

        for p in CONTAMINANTES:
            if not pollutant_validity[p]:
                continue

            ratio = ratios_row[p]

            if not is_valid_number(ratio) or float(ratio) == 0:
                continue

            inferred = float(row[p]) * float(ratio)
            inferred_values.append(inferred)

        if inferred_values:
            # Average the inferred pm25 values
            row["pm25"] = sum(inferred_values) / len(inferred_values)
            new_rows.append(row)
            continue

        # CASE D — cannot infer pm25 → fallback to previous complete row
        if previous_complete is not None:
            for c in ["pm25"] + CONTAMINANTES:
                row[c] = previous_complete[c]
            new_rows.append(row)
            continue

        # CASE E — cannot infer and no backup → delete row
        continue

    # CREATE OUTPUT FILE — overwrite if exists
    out_file = file_path.replace(".csv", "_inferred.csv")
    out_df = pd.DataFrame(new_rows)
    out_df.to_csv(out_file, sep=';', index=False)

    print(f"Inference completed → {out_file}")


if __name__ == "__main__":
    main()
