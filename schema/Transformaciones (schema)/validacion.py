import rdflib
import glob
import os

# CONFIGURACIÓN
carpeta_datos = "archivos_ttl"
patron = os.path.join(carpeta_datos, "*.ttl")

print(f"INICIANDO VALIDACIÓN EXHAUSTIVA EN: {carpeta_datos}...\n")

g = rdflib.Graph()
archivos = glob.glob(patron)

if not archivos:
    print("ERROR: No hay archivos .ttl en la carpeta.")
    exit()

# 1. CARGA
for archivo in archivos:
    try:
        g.parse(archivo, format="turtle")
    except Exception as e:
        print(f"ERROR CRÍTICO leyendo {os.path.basename(archivo)}: {e}")

print(f"OK Carga completada. Analizando {len(g)} tripletas...\n")

# --- CHECK 1: INTEGRIDAD DE REGIONES (EL MÁS IMPORTANTE) ---
print("1. Comprobando coherencia de Regiones (Cruzar datos vs. Wikidata)...")

# A. Sacamos todas las regiones que aparecen en tus DATOS (Gini, Población, etc.)
q_datos = """
    SELECT DISTINCT ?region
    WHERE { 
        ?obs a <https://schema.org/Observation> ;
             <https://schema.org/observedNode> ?region .
    }
"""
regiones_en_datos = set([str(row.region) for row in g.query(q_datos)])

# B. Sacamos todas las regiones que tienen ENLACE a Wikidata
q_wiki = """
    SELECT DISTINCT ?region
    WHERE { 
        ?region <http://www.w3.org/2002/07/owl#sameAs> ?link .
    }
"""
regiones_con_enlace = set([str(row.region) for row in g.query(q_wiki)])

# C. Comparamos
regiones_sin_enlace = regiones_en_datos - regiones_con_enlace

if len(regiones_sin_enlace) == 0:
    print("OK PERFECTO: Todas las regiones usadas en los datos tienen su enlace a Wikidata.")
else:
    print(f"ERROR ALERTA: Hay {len(regiones_sin_enlace)} regiones con datos pero SIN enlace a Wikidata (Revisa nombres):")
    for r in regiones_sin_enlace:
        print(f"      - {r.split('/')[-1]} (Existe en CSVs pero no en el script de enlaces)")

# --- CHECK 2: OBSERVACIONES INCOMPLETAS ---
print("\n2. Buscando observaciones rotas (que les falte algo)...")
q_incompletas = """
    SELECT ?obs
    WHERE { 
        ?obs a <https://schema.org/Observation> .
        FILTER (
            NOT EXISTS { ?obs <https://schema.org/observationDate> ?date } ||
            NOT EXISTS { ?obs <https://schema.org/value> ?val } ||
            NOT EXISTS { ?obs <https://schema.org/observedNode> ?node }
        )
    }
"""
rotas = list(g.query(q_incompletas))
if len(rotas) == 0:
    print("   OK PERFECTO: Todas las observaciones están completas.")
else:
    print(f"   ERROR ERROR: Se han encontrado {len(rotas)} observaciones incompletas.")

# --- CHECK 3: CALIDAD DE VALORES NUMÉRICOS ---
print("\n3. Validando tipos de datos numéricos...")
q_bad_numbers = """
    SELECT ?val
    WHERE { 
        ?obs <https://schema.org/value> ?val .
        FILTER (DATATYPE(?val) != <http://www.w3.org/2001/XMLSchema#float> && 
                DATATYPE(?val) != <http://www.w3.org/2001/XMLSchema#integer>)
    }
"""
bad_nums = list(g.query(q_bad_numbers))
if len(bad_nums) == 0:
    print("OK PERFECTO: Todos los valores están tipados correctamente como números.")
else:
    print(f"ERROR AVISO: Hay {len(bad_nums)} valores que no son numéricos (quizás sean texto).")

print("\n--- FIN DEL ANÁLISIS ---")