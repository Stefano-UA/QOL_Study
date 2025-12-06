import pandas as pd
import os  

# 1. CARGA DE DATOS
# Leemos el archivo específico de PIBC dentro de la carpeta 'csvs'
df = pd.read_csv('csvs/pibc_ccaa.csv', sep='\t')

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
    
    # Variable: Limpiamos paréntesis, espacios, etc.
    var_raw = row['Type']
    var_clean = var_raw.replace("(", "").replace(")", "").replace("/", "_").replace(" ", "_").lower()
    
    # --- LIMPIEZA DE VALOR (CASO ESPECIAL RENTA) ---
    # En este CSV, "13.859" significa 13 mil.
    # 1. Quitamos el punto de los miles: "13.859" -> "13859"
    # 2. Si hubiera comas decimales, las cambiamos por puntos.
    value_str = str(row['Value']).replace('.', '').replace(',', '.')
    
    # --- CONSTRUCCIÓN ---
    subject = f"ex:{ccaa_clean}_{year}_{var_clean}"
    
    ttl_content += f"{subject} a schema:Observation ;\n"
    
    # Prefijo semántico 'economic_'
    ttl_content += f"    schema:measuredProperty ex:economic_{var_clean} ;\n"
    
    ttl_content += f'    schema:observationDate "{year}"^^xsd:gYear ;\n'
    ttl_content += f"    schema:observedNode ex:Region_{ccaa_clean} ;\n"
    ttl_content += f'    schema:value "{value_str}"^^xsd:float .\n\n'

# 4. GUARDAR EL ARCHIVO EN LA CARPETA 'archivos_ttl'
carpeta_salida = "archivos_ttl"

if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

nombre_archivo = "pibc_ccaa.ttl"
ruta_completa = os.path.join(carpeta_salida, nombre_archivo)

with open(ruta_completa, "w", encoding="utf-8") as f:
    f.write(ttl_content)

print(f"¡Listo! Archivo guardado correctamente en: {ruta_completa}")
print(f"URI Base utilizada: {BASE_URI}")