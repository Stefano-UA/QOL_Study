import pandas as pd
import os  

# 1. CARGA DE DATOS
# Leemos el archivo de Población dentro de la carpeta 'csvs'
df = pd.read_csv('csvs/pob_ccaa.csv', sep='\t')

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
    # Como este CSV no tiene columna 'Type', definimos nosotros la variable.
    var_clean = "population" 
    
    # --- CAMBIO 2: LIMPIEZA DE NÚMEROS DE POBLACIÓN ---
    # El dato viene como "8.484.804" (miles con puntos).
    # 1. Quitamos los puntos de los miles.
    # 2. Si hubiera algún decimal con coma, lo cambiamos a punto.
    value_str = str(row['Value']).replace('.', '').replace(',', '.')
    
    # --- CONSTRUCCIÓN DEL ID (SUJETO) ---
    subject = f"ex:{ccaa_clean}_{year}_{var_clean}"
    
    # --- BLOQUE DE DATOS ---
    ttl_content += f"{subject} a schema:Observation ;\n"
    
    # Prefijo semántico 'demographic_'
    ttl_content += f"    schema:measuredProperty ex:{var_clean} ;\n"
    
    ttl_content += f'    schema:observationDate "{year}"^^xsd:gYear ;\n'
    ttl_content += f"    schema:observedNode ex:Region_{ccaa_clean} ;\n"
    
    # Nota: Usamos float por consistencia con el resto, aunque sea entero.
    ttl_content += f'    schema:value "{value_str}"^^xsd:float .\n\n'

# 4. GUARDAR EL ARCHIVO EN LA CARPETA 'archivos_ttl'
carpeta_salida = "archivos_ttl"

if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

nombre_archivo = "pob_ccaa.ttl"
ruta_completa = os.path.join(carpeta_salida, nombre_archivo)

with open(ruta_completa, "w", encoding="utf-8") as f:
    f.write(ttl_content)

print(f"¡Listo! Archivo guardado correctamente en: {ruta_completa}")
print(f"URI Base utilizada: {BASE_URI}")