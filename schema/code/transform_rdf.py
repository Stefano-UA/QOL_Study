# transform_rdf.py
import pandas as pd
import os
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

# Configuración de rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(SCRIPT_DIR, "../dist/kettle")
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, "../schema")

# Namespaces
SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://grupo3-ua-data.github.io/resource/")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")

# Mapeo CCAA -> Wikidata
ccaa_wikidata_map = {
  "andalucia": "Q5718", "aragon": "Q4040", "asturias": "Q3934",
  "baleares": "Q4071", "canarias": "Q5709", "cantabria": "Q3946",
  "castilla_la_mancha": "Q5748", "castilla_leon": "Q5739",
  "catalunya": "Q5705", "ceuta": "Q5823", "comunidad_valenciana": "Q5720",
  "extremadura": "Q5777", "galicia": "Q3911", "la_rioja": "Q5727",
  "madrid": "Q5756", "melilla": "Q5831", "murcia": "Q5768",
  "navarra": "Q4018", "pais_vasco": "Q3995", "rioja": "Q5727",
  "total_nacional": "Q29"
}

# Funciones de limpieza
def clean_spanish_number(val):
  """Limpia números formato español (1.200,50 -> 1200.5)"""
  if isinstance(val, (int, float)): return val
  val = str(val)
  if '.' in val and ',' in val:
    val = val.replace('.', '').replace(',', '.')
  elif ',' in val:
    val = val.replace(',', '.')
  elif '.' in val: # Asumimos miles si no hay coma
    val = val.replace('.', '')
  try:
    return float(val)
  except:
    return 0.0

def clean_english_number(val):
  """Limpia números formato inglés (1200.50 -> 1200.5)"""
  try:
    return float(val)
  except:
    return 0.0

def process_file(filename, config):
  csv_path = os.path.join(DATA_FOLDER, filename)
  
  # Comprobación de existencia
  if not os.path.exists(csv_path):
    print(f"NO ENCONTRADO: {csv_path}")
    print(f"'{filename}' no está en 'dist/kettle'")
    return

  print(f"Procesando {filename}...")
  
  try:
    # Detectar separador automáticamente
    df = pd.read_csv(csv_path, sep=None, engine='python')
  except Exception as e:
    print(f"Error leyendo {filename}: {e}")
    return

  # Filtrado de filas
  if 'filter_col' in config:
    df = df[df[config['filter_col']] == config['filter_val']]

  g = Graph()
  g.bind("schema", SCHEMA)
  g.bind("ex", EX)
  g.bind("owl", OWL)
  
  count = 0
  for index, row in df.iterrows():
    try:
      # Obtención de columnas
      year = str(row.get('Year', row.get('Periodo', row.get('YEAR', '2024'))))
      ccaa_raw = row.get('CCAA', row.get('Comunidad', 'Desconocido'))
      
      # Valor numérico
      val_raw = row.get('Value', row.get('Total', 0))
      if config['number_format'] == 'spanish':
        val_num = clean_spanish_number(val_raw)
      else:
        val_num = clean_english_number(val_raw)

      # Normalización ID
      ccaa_clean = str(ccaa_raw).lower().strip().replace(' ', '_')
      
      # Tripletas
      # 1. Entidad Geográfica
      uri_lugar = EX[f"Place/{ccaa_clean}"]
      g.add((uri_lugar, RDF.type, SCHEMA.AdministrativeArea))
      g.add((uri_lugar, SCHEMA.name, Literal(ccaa_raw)))
      
      if ccaa_clean in ccaa_wikidata_map:
        g.add((uri_lugar, OWL.sameAs, WIKIDATA[ccaa_wikidata_map[ccaa_clean]]))

      # 2. Observación Estadística
      obs_id = f"{config['var_name']}_{ccaa_clean}_{year}"
      uri_obs = EX[f"Observation/{obs_id}"]

      g.add((uri_obs, RDF.type, SCHEMA.Observation))
      g.add((uri_obs, SCHEMA.variableMeasured, Literal(config['var_full_name'])))
      g.add((uri_obs, SCHEMA.value, Literal(val_num, datatype=XSD.float)))
      g.add((uri_obs, SCHEMA.unitText, Literal(config['unit'])))
      g.add((uri_obs, SCHEMA.observationDate, Literal(year, datatype=XSD.gYear)))
      g.add((uri_obs, SCHEMA.areaServed, uri_lugar))

      count += 1
    except Exception as e:
      continue

  # Exportar
  if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
  out_file = os.path.join(OUTPUT_FOLDER, f"rdf_{config['var_name']}.ttl")
  g.serialize(destination=out_file, format="turtle")
  print(f"Generado: {out_file} ({count} tripletas)")

# Configuración de archivos
files_to_process = [
  {'filename': 'gini_ccaa.csv',
   'var_name': 'gini',
   'var_full_name': 'Índice Gini',
   'unit': 'Index',
   'number_format': 'spanish',
   'filter_col': 'Type', 'filter_val': 'gini'},
  {'filename': 'pob_ccaa.csv',
   'var_name': 'poblacion',
   'var_full_name': 'Población Total',
   'unit': 'Personas',
   'number_format': 'spanish'},
  {'filename': 'qol_ccaa.csv',
   'var_name': 'calidad_vida',
   'var_full_name': 'Índice Calidad de Vida',
   'unit': 'Index',
   'number_format': 'english'},
  {'filename': 'ipca_ccaa.csv',
   'var_name': 'ipc',
   'var_full_name': 'IPC General',
   'unit': 'Index',
   'number_format': 'english',
   'filter_col': 'ECOICOP', 'filter_val': 'indice_general'},
  {'filename': 'pibc_ccaa.csv',
   'var_name': 'renta_media',
   'var_full_name': 'Renta Neta Media',
   'unit': 'Euro',
   'number_format': 'spanish',
   'filter_col': 'Type', 'filter_val': 'renta_neta_media_por_persona'}
]

if __name__ == "__main__":
  print(f"Buscando archivos en: {os.path.abspath(DATA_FOLDER)}")
  for f_config in files_to_process:
    process_file(f_config['filename'], f_config)