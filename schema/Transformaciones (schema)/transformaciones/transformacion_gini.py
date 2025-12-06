import pandas as pd
import os 

# 1. CARGA DE DATOS
# Leemos desde la carpeta 'csvs'
df = pd.read_csv('csvs/gini_ccaa.csv', sep='\t')

# 2. CONFIGURACIÓN DEL PREFIJO
BASE_URI = "https://github.com/csalas-alarcon/Grupo3_ADP/"

ttl_content = f"""@prefix ex: <{BASE_URI}> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

# 3. GENERACIÓN DE TRIPLETAS
for index, row in df.iterrows():
    # Limpieza de datos
    year = str(row['Year'])
    # CCAA: minusculas y sin espacios
    ccaa_clean = row['CCAA'].replace(" ", "_").lower()
    
    # Variable: limpiamos paréntesis y barras
    var_raw = row['Type']
    var_clean = var_raw.replace("(", "").replace(")", "").replace("/", "_").replace(" ", "_").lower()
    
    # Valor: coma por punto
    value_str = str(row['Value']).replace(',', '.')
    
    # --- CONSTRUCCIÓN DEL ID (SUJETO) ---
    subject = f"ex:{ccaa_clean}_{year}_{var_clean}"
    
    # --- BLOQUE DE DATOS ---
    ttl_content += f"{subject} a schema:Observation ;\n"
    
    # Propiedad específica
    ttl_content += f"    schema:measuredProperty ex:inequality_{var_clean} ;\n"
    
    # Fecha
    ttl_content += f'    schema:observationDate "{year}"^^xsd:gYear ;\n'
    
    # Nodo Observado (Lugar)
    ttl_content += f"    schema:observedNode ex:Region_{ccaa_clean} ;\n"
    
    # Valor numérico
    ttl_content += f'    schema:value "{value_str}"^^xsd:float .\n\n'

# 4. GUARDAR EL ARCHIVO EN LA CARPETA 'archivos_ttl'
carpeta_salida = "archivos_ttl"

# Si la carpeta no existe, la creamos automáticamente
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

nombre_archivo = "gini_ccaa.ttl"
ruta_completa = os.path.join(carpeta_salida, nombre_archivo)

with open(ruta_completa, "w", encoding="utf-8") as f:
    f.write(ttl_content)

print(f"¡Listo! Archivo guardado correctamente en: {ruta_completa}")
print(f"URI Base utilizada: {BASE_URI}")