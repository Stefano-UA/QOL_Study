import pandas as pd
import os  

# 1. CARGA DE DATOS
# Leemos el archivo específico de IPCA dentro de la carpeta 'csvs'
df = pd.read_csv('csvs/ipca_ccaa.csv', sep='\t')

# 2. CONFIGURACIÓN DEL PREFIJO
BASE_URI = "https://github.com/csalas-alarcon/Grupo3_ADP/"

ttl_content = f"""@prefix ex: <{BASE_URI}> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

# 3. GENERACIÓN DE TRIPLETAS
for index, row in df.iterrows():
    # Limpieza de datos básicos
    year = str(row['Year'])
    ccaa_clean = row['CCAA'].replace(" ", "_").lower()
    
    # --- CAMBIO IMPORTANTE PARA IPCA ---
    # Juntamos ECOICOP + Type para tener una variable única
    
    # 1. Limpiamos la categoría (ECOICOP)
    eco_raw = str(row['ECOICOP'])
    eco_clean = eco_raw.replace("(", "").replace(")", "").replace("/", "_").replace(" ", "_").replace(",", "").lower()
    
    # 2. Limpiamos el tipo (indice / variacion)
    type_raw = str(row['Type'])
    type_clean = type_raw.replace("(", "").replace(")", "").replace("/", "_").replace(" ", "_").lower()
    
    # 3. Variable final combinada
    var_clean = f"{eco_clean}_{type_clean}"
    
    # Valor: coma por punto
    value_str = str(row['Value']).replace(',', '.')
    
    # --- CONSTRUCCIÓN DEL ID (SUJETO) ---
    subject = f"ex:{ccaa_clean}_{year}_{var_clean}"
    
    # --- BLOQUE DE DATOS ---
    ttl_content += f"{subject} a schema:Observation ;\n"
    
    # Propiedad: Usamos el prefijo 'ipca_'
    ttl_content += f"    schema:measuredProperty ex:{var_clean} ;\n"
    
    ttl_content += f'    schema:observationDate "{year}"^^xsd:gYear ;\n'
    
    # Nodo Observado (Lugar)
    ttl_content += f"    schema:observedNode ex:Region_{ccaa_clean} ;\n"
    
    ttl_content += f'    schema:value "{value_str}"^^xsd:float .\n\n'

# 4. GUARDAR EL ARCHIVO EN LA CARPETA 'archivos_ttl'
carpeta_salida = "archivos_ttl"

# Si la carpeta no existe, la creamos
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

nombre_archivo = "ipca_ccaa.ttl"
ruta_completa = os.path.join(carpeta_salida, nombre_archivo)

with open(ruta_completa, "w", encoding="utf-8") as f:
    f.write(ttl_content)

print(f"¡Listo! Archivo guardado correctamente en: {ruta_completa}")
print(f"URI Base utilizada: {BASE_URI}")