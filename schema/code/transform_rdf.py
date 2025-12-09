import pandas as pd
import os
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

# --- CONFIGURACION DE RUTAS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(SCRIPT_DIR, "../../dist/kettle")
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, "..")

# --- NAMESPACES ---
BASE_URI = "https://csalas-alarcon.github.io/Grupo3_ADP/ontology/"
SCHEMA = Namespace("http://schema.org/")
EX = Namespace(BASE_URI)
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")

# --- MAPEO CCAA -> WIKIDATA ---
ccaa_wikidata_map = {
    "andalucia": "Q5718", "aragon": "Q4040", "asturias": "Q3934",
    "baleares": "Q4071", "canarias": "Q5709", "cantabria": "Q3946",
    "castilla_la_mancha": "Q5748", "castilla_leon": "Q5739",
    "catalunya": "Q5705", "ceuta": "Q5823", "comunidad_valenciana": "Q5720",
    "extremadura": "Q5777", "galicia": "Q3911", "la_rioja": "Q5727",
    "madrid": "Q5756", "melilla": "Q5831", "murcia": "Q5768",
    "navarra": "Q4018", "pais_vasco": "Q3995", "rioja": "Q5727",
    "total_nacional": "Q29", "total": "Q29"
}

# --- FUNCIONES DE LIMPIEZA ---
def clean_spanish_number(val):
    if isinstance(val, (int, float)): return val
    val = str(val).strip()
    if '.' in val and ',' in val:
        val = val.replace('.', '').replace(',', '.')
    elif ',' in val:
        val = val.replace(',', '.')
    elif '.' in val:
        val = val.replace('.', '')
    try:
        return float(val)
    except:
        return 0.0

def clean_english_number(val):
    try:
        val = str(val).replace(',', '.') # Por si acaso se cuela alguna coma
        return float(val)
    except:
        return 0.0

def process_file(config):
    filename = config['filename']
    csv_path = os.path.join(DATA_FOLDER, filename)
    
    if not os.path.exists(csv_path):
        print(f"NO ENCONTRADO: {filename}")
        return

    print(f"Procesando {filename}...")
    
    try:
        # Detectamos separador automáticamente (tus archivos usan tabuladores o comas según el caso)
        df = pd.read_csv(csv_path, sep=None, engine='python')
    except Exception as e:
        print(f"Error leyendo {filename}: {e}")
        return

    g = Graph()
    g.bind("schema", SCHEMA)
    g.bind("ex", EX)
    g.bind("owl", OWL)
    
    count = 0
    
    # Obtenemos el nombre de la columna que define el tipo (por defecto 'Type')
    type_col = config.get('type_col', 'Type')

    for index, row in df.iterrows():
        try:
            # --- 1. DETERMINAR ETIQUETAS Y SLUGS ---
            if 'mappings' in config:
                # El archivo tiene múltiples tipos (ej: Gini y S80/20)
                row_type = row.get(type_col)
                
                # Si el tipo de la fila no está en nuestro mapa, lo ignoramos (o reportamos error)
                if row_type not in config['mappings']:
                    continue 

                mapping = config['mappings'][row_type]
                var_slug = mapping['slug']
                var_label = mapping['label']
                var_unit = mapping['unit']
            else:
                # El archivo es simple (solo un dato, ej: Población)
                var_slug = config['default_slug']
                var_label = config['default_label']
                var_unit = config['default_unit']

            # --- 2. EXTRAER VALORES ---
            year = str(row.get('Year', row.get('YEAR', '2024')))
            ccaa_raw = row.get('CCAA', 'Desconocido')
            val_raw = row.get('Value', 0)

            if config['number_format'] == 'spanish':
                val_num = clean_spanish_number(val_raw)
            else:
                val_num = clean_english_number(val_raw)

            ccaa_clean = str(ccaa_raw).lower().strip().replace(' ', '_')
            
            # --- 3. GENERAR TRIPLETAS RDF ---

            # A) LUGAR (Place)
            uri_lugar = EX[f"Region_{ccaa_clean}"]
            g.add((uri_lugar, RDF.type, SCHEMA.Place))
            g.add((uri_lugar, SCHEMA.name, Literal(ccaa_raw)))
            
            if ccaa_clean in ccaa_wikidata_map:
                g.add((uri_lugar, OWL.sameAs, WIKIDATA[ccaa_wikidata_map[ccaa_clean]]))

            # B) OBSERVACIÓN (Observation)
            # El ID debe ser único: VARIABLE + LUGAR + AÑO
            # Ej: observation/gini_andalucia_2022 vs observation/s80_s20_andalucia_2022
            obs_id = f"{var_slug}_{ccaa_clean}_{year}"
            uri_obs = EX[f"Observation/{obs_id}"]

            g.add((uri_obs, RDF.type, SCHEMA.Observation))
            g.add((uri_obs, SCHEMA.variableMeasured, Literal(var_label)))
            g.add((uri_obs, SCHEMA.value, Literal(val_num, datatype=XSD.float)))
            g.add((uri_obs, SCHEMA.unitText, Literal(var_unit)))
            g.add((uri_obs, SCHEMA.observationDate, Literal(year, datatype=XSD.gYear)))
            g.add((uri_obs, SCHEMA.areaServed, uri_lugar))

            count += 1
        except Exception as e:
            continue

    # --- 4. GUARDAR ARCHIVO ÚNICO ---
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    out_file = os.path.join(OUTPUT_FOLDER, config['output_name'])
    g.serialize(destination=out_file, format="turtle")
    print(f" -> Generado: {config['output_name']} ({count} tripletas)")

# --- CONFIGURACION DE ARCHIVOS (Mapeos basados en CSVs) ---
files_to_process = [
    # 1. GINI + DESIGUALDAD (Mismo archivo, dos tipos)
    {
        'filename': 'gini_ccaa.csv',
        'output_name': 'rdf_gini.ttl',
        'number_format': 'spanish',
        'type_col': 'Type',
        'mappings': {
            'gini': {'slug': 'gini', 'label': 'Indice Gini', 'unit': 'Index'},
            'desigualdad_(s80/s20)': {'slug': 's80_s20', 'label': 'Ratio S80/S20', 'unit': 'Ratio'}
        }
    },
    
    # 2. IPC (Indice General + Variación Anual)
    {
        'filename': 'ipca_ccaa.csv',
        'output_name': 'rdf_ipca.ttl',
        'number_format': 'spanish', 
        'type_col': 'Type',
        'mappings': {
            'indice': {'slug': 'ipc_indice', 'label': 'IPC Indice General', 'unit': 'Index'},
            'variacion_anual': {'slug': 'ipc_var', 'label': 'IPC Variacion Anual', 'unit': 'Percentage'}
        }
    },
    
    # 3. RENTA (Por persona + Por unidad de consumo)
    {
        'filename': 'pibc_ccaa.csv',
        'output_name': 'rdf_pibc.ttl',
        'number_format': 'spanish',
        'type_col': 'Type',
        'mappings': {
            'renta_neta_media_por_persona': {'slug': 'renta_persona', 'label': 'Renta Neta Media por Persona', 'unit': 'Euro'},
            'renta_media_por_unidad_de_consumo': {'slug': 'renta_consumo', 'label': 'Renta Media Unidad Consumo', 'unit': 'Euro'}
        }
    },

    # 4. POBLACION (Archivo simple, sin columna Type)
    {
        'filename': 'pob_ccaa.csv',
        'output_name': 'rdf_pob.ttl',
        'number_format': 'spanish', # 5990874 
        'default_slug': 'poblacion',
        'default_label': 'Poblacion Total',
        'default_unit': 'Personas'
    },
    
    # 5. CALIDAD DE VIDA 
    {
        'filename': 'qol_ccaa.csv',
        'output_name': 'rdf_qol.ttl',
        'number_format': 'spanish', # 97,9101... (usa coma)
        'default_slug': 'calidad_vida',
        'default_label': 'Indice Calidad de Vida',
        'default_unit': 'Index'
    }
]

if __name__ == "__main__":
    print(f"Buscando archivos en: {os.path.abspath(DATA_FOLDER)}")
    for f_config in files_to_process:

        process_file(f_config)

