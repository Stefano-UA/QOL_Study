import sys
import os
import pandas as pd

# Constantes globales
CONTAMINANTES = ["pm10", "o3", "no2", "so2", "co"]

# --- Funciones Auxiliares ---

def is_valid_number(x):
    """Return True if x is a number >= 0."""
    try:
        v = float(x)
        return v >= 0
    except:
        return False

# La función load_ratios de inferencia25 se convierte en load_single_ratio_row
def load_single_ratio_row(region, file_path):
    """Carga la fila de ratios específica para el ID del archivo."""
    base_id = os.path.basename(file_path)[:10]
    ratio_csv = os.path.join("../../temp/pollution", region, f"{region}_ratios.csv")

    if not os.path.isfile(ratio_csv):
        print(f"ERROR: ARCHIVO RATIO NO ENCONTRADO: {ratio_csv}")
        sys.exit(1)

    df_rat = pd.read_csv(ratio_csv, sep=';')

    if "id" not in df_rat.columns:
        print("ERROR: EL ARCHIVO DE RATIOS NO TIENE COLUMNA 'ID'")
        sys.exit(1)

    match = df_rat[df_rat["id"].astype(str) == base_id]

    if match.empty:
        print(f"ERROR: RATIO NO ENCONTRADO PARA ID: {base_id} EN {ratio_csv}")
        sys.exit(1)

    return match.iloc[0]


def get_ratio_for_pollutant(df_ratios, file_id, pollutant):
    """
    Obtiene el ratio: prioritiza el ID del archivo; sino, usa el ID de fallback 'ZZZZZZZZZZ'.
    Se eliminan los bucles lentos de iteración.
    """
    # 1. INTENTO DE MATCH POR ID ESPECÍFICO (Prioridad Alta)
    match_id = df_ratios[df_ratios["id"].astype(str) == file_id]
    
    if not match_id.empty:
        ratio = match_id.iloc[0].get(pollutant)
        if is_valid_number(ratio) and float(ratio) > 0:
            return float(ratio)

    # 2. FALLBACK AL ID DE SEGURIDAD 'ZZZZZZZZZZ' (Búsqueda Directa)
    fallback_id = "ZZZZZZZZZZ"
    match_fallback = df_ratios[df_ratios["id"].astype(str) == fallback_id]
    
    if not match_fallback.empty:
        ratio = match_fallback.iloc[0].get(pollutant)
        if is_valid_number(ratio) and float(ratio) > 0:
            return float(ratio)
        else:
            # Si se encuentra el ID de fallback pero el ratio es inválido (ej: 0 o NaN)
            print(f"ADVERTENCIA: Ratio inválido para {pollutant} en la fila de fallback {fallback_id}.")
            return None # Devolver None para que el flujo principal falle con ERROR

    # 3. FRACASO TOTAL (Ni ID específico, ni fallback encontrado/válido)
    return None


# --- Función Principal Unificada ---

def main():
    if len(sys.argv) != 3:
        print("Uso: inferenciaCompleta.py <region> <file.csv>")
        sys.exit(1)

    region = sys.argv[1]
    file_path = sys.argv[2]
    
    if not os.path.isfile(file_path):
        print(f"ERROR: ARCHIVO NO ENCONTRADO: {file_path}")
        sys.exit(1)

    # 1. CARGA DE RATIOS
    # Cargamos la fila específica de PM2.5 (usada en la Primera Etapa)
    pm25_ratios_row = load_single_ratio_row(region, file_path)

    # Cargamos el DataFrame completo de ratios (usado en la Segunda Etapa)
    ratio_csv = os.path.join("../../temp/pollution", region, f"{region}_ratios.csv")
    try:
        df_ratios_full = pd.read_csv(ratio_csv, sep=';')
    except Exception as e:
        print(f"ERROR: No se puede leer el csv de ratios: {e}")
        sys.exit(1)
    
    file_id = os.path.basename(file_path)[:10]

    # 2. CARGA DE DATOS
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"ERROR: NO SE PUEDE LEER {file_path} : {e}")
        sys.exit(1)

    # Chequeo columnas (PM2.5 y Contaminantes)
    for col in ["pm25"] + CONTAMINANTES:
        if col not in df.columns:
            df[col] = pd.NA

    new_rows = []
    
    # 3. PRIMERA ETAPA: INFERENCIA PM2.5 (Lógica de inferencia25.py)
    print("----Inferencia de PM25: ")
    for idx, row in df.iterrows():
        row = row.copy()
        pm25_valid = is_valid_number(row["pm25"])

        pollutant_validity = {
            p: is_valid_number(row[p]) and float(row[p]) > 0
            for p in CONTAMINANTES
        }
        num_valid_pollutants = sum(pollutant_validity.values())

        # CASE A/D: BORRAMOS (nada valido)
        if (not pm25_valid) and num_valid_pollutants == 0:
            continue

        # CASE B: SALTAMOS (pm25 ya es valido)
        if pm25_valid:
            # Mantener row.copy() para la segunda etapa
            new_rows.append(row)
            continue

        # CASE C: INFERENCIA (falta pm25)
        inferred_values = []

        for p in CONTAMINANTES:
            if not pollutant_validity[p]:
                continue

            ratio = pm25_ratios_row[p]
            if not is_valid_number(ratio) or float(ratio) == 0:
                continue

            inferred = float(row[p]) * float(ratio)
            inferred_values.append(inferred)

        if inferred_values:
            row["pm25"] = sum(inferred_values) / len(inferred_values)
            new_rows.append(row)
            continue
        
        # Si llega aquí, es un caso D que no pudo inferirse y se descarta

    # Actualizamos el DataFrame con las filas filtradas e inferidas
    df_inferred_pm25 = pd.DataFrame(new_rows)
    
    # 4. SEGUNDA ETAPA: INFERENCIA OTROS CONTAMINANTES (Lógica de inferenciaContaminantes.py)
    print("----Inferencia del Resto de Contaminantes")
    final_rows = []
    
    for idx, row in df_inferred_pm25.iterrows():
        row = row.copy()

        # En este punto, 'pm25' debe ser válido debido al filtrado de la Etapa 1
        if not is_valid_number(row["pm25"]):
             # Esto no debería ocurrir si la Etapa 1 funciona correctamente, pero es una salvaguarda.
             print(f"ERROR CRÍTICO: Valor pm25 inválido después de la inferencia en fila: {idx}")
             sys.exit(1)

        pm25_value = float(row["pm25"])

        # Procesamos cada contaminante
        for pollutant in CONTAMINANTES:
            if is_valid_number(row[pollutant]):
                continue 

            ratio = get_ratio_for_pollutant(df_ratios_full, file_id, pollutant)
            if ratio is None:
                print(f"ERROR: No se puede inferir {pollutant} para la fila {idx} por que no hay ratio valido")
                sys.exit(1)

            # Inferencia del Contaminante
            row[pollutant] = pm25_value / ratio

        final_rows.append(row)
    
    # 5. ESCRITURA FINAL
    out_df = pd.DataFrame(final_rows)
    
    # Sobreescribir el archivo original con los datos completamente inferidos
    try:
        out_df.to_csv(file_path, sep=';', index=False)
        print("ÉXITO")
        print(f"Inferencia Completa, el CSV actualizado es: \n{file_path}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar: {file_path} porque {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()