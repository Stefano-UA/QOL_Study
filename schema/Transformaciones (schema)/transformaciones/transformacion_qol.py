import pandas as pd
import os  # <--- IMPORTANTE

# 1. CARGA DE DATOS
# Leemos el archivo de Calidad de Vida
df = pd.read_csv('csvs/qol_ccaa.csv', sep='\t')

# 2. CONFIGURACIÓN DEL PREFIJO
BASE_URI = "https://github.com/csalas-alarcon/Grupo3_ADP/"

ttl_content = f"""@prefix ex: <{BASE_URI}> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

# 3. GENERACIÓN DE TRIPLETAS
for index, row in df.iterrows():
    year = str(row['Year'])
    ccaa_clean = row['CCAA'].replace(" ", "_").lower()
    
    # --- CAMBIO 1: VARIABLE FIJA ---
    var_clean = "quality_of_life"
    
    # --- CAMBIO 2: VALORES DECIMALES (IMPORTANTE) ---
    # En este CSV, "97.91" es un decimal. NO quitamos el punto.
    # Solo reemplazamos la coma por punto (por seguridad).
    value_str = str(row['Value']).replace(',', '.')
    
    # --- CONSTRUCCIÓN DEL ID (SUJETO) ---
    subject = f"ex:{ccaa_clean}_{year}_{var_clean}"
    
    # --- BLOQUE DE DATOS ---
    ttl_content += f"{subject} a schema:Observation ;\n"
    
    # Prefijo semántico 'social_'
    ttl_content += f"    schema:measuredProperty ex:{var_clean} ;\n"
    
    ttl_content += f'    schema:observationDate "{year}"^^xsd:gYear ;\n'
    ttl_content += f"    schema:observedNode ex:Region_{ccaa_clean} ;\n"
    ttl_content += f'    schema:value "{value_str}"^^xsd:float .\n\n'

# 4. GUARDAR EL ARCHIVO EN LA CARPETA 'archivos_ttl'
carpeta_salida = "archivos_ttl"

if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

nombre_archivo = "qol_ccaa.ttl"
ruta_completa = os.path.join(carpeta_salida, nombre_archivo)

with open(ruta_completa, "w", encoding="utf-8") as f:
    f.write(ttl_content)

print(f"¡Listo! Archivo guardado correctamente en: {ruta_completa}")
print(f"URI Base utilizada: {BASE_URI}")