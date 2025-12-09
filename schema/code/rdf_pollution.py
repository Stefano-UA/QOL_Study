import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD, OWL
import re

# --- Namespaces RDF ---
SCHEMA = Namespace("https://schema.org/")
BASE_URI = "https://csalas-alarcon.github.io/Grupo3_ADP/"
EX = Namespace(BASE_URI + "ontology/")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
ENVO = Namespace("http://purl.obolibrary.org/obo/ENVO_")
CHEBI = Namespace("http://purl.obolibrary.org/obo/CHEBI_")

# --- Mapping CCAA -> Wikidata ---
ccaa_wikidata_map = {
    "andalucia": "Q5718", "aragon": "Q4040", "asturias": "Q3934",
    "baleares": "Q4071", "canarias": "Q5709", "cantabria": "Q3946",
    "castilla_la_mancha": "Q5748", "castilla_leon": "Q5739",
    "catalunya": "Q5705", "ceuta": "Q5823", "comunidad_valenciana": "Q5720",
    "extremadura": "Q5777", "galicia": "Q3911", "rioja": "Q5727",
    "madrid": "Q5756", "melilla": "Q5831", "murcia": "Q5768",
    "navarra": "Q4018", "pais_vasco": "Q3995", "total_nacional": "Q29"
}

# --- Mapeo Contaminantes -> URI Concepto + unidades ---
UNIT_MAP = {
    "pm25": "UGM3",
    "pm10": "UGM3",
    "o3": "PPB",
    "no2": "PPB",
    "so2": "PPB",
    "co": "PPM"
}

# --- Mapeo Contaminantes Medición ---
POLLUTANT_CONCEPT_MAP = {
    "pm25": ENVO["01000305"],  
    "pm10": ENVO["01000306"], 
    "o3": CHEBI["16314"],    
    "no2": CHEBI["33104"],    
    "so2": CHEBI["18428"],     
    "co": CHEBI["16314"]       
}

# --- Rutas ---
INPUT_CSV = "../dist/kettle/pollution.csv"
OUTPUT_TTL = "../schema/pollution.ttl"

# --- Leer CSV ---
df = pd.read_csv(INPUT_CSV, sep='\t')

# --- Crear grafo RDF ---
g = Graph()
g.bind("schema", SCHEMA)
g.bind("ex", EX)
g.bind("owl", OWL)
g.bind("envo", ENVO)      
g.bind("chebi", CHEBI)    

# --- Iterar sobre cada fila ---
for idx, row in df.iterrows():
    year = str(row["Year"])
    ccaa = str(row["CCAA"])
    pol = str(row["Type"])
    value = row["Value"]

    # Limpiar nombre para URI
    ccaa_clean = re.sub("_+", "_", ccaa.strip().replace(" ", "_"))
    pol_clean = re.sub("_+", "_", pol.strip().replace(" ", "_"))

    # URI del lugar (sin cambios)
    region_uri = EX[f"Region_{ccaa_clean}"]
    g.add((region_uri, RDF.type, SCHEMA.Place))
    g.add((region_uri, SCHEMA.name, Literal(ccaa)))

    # Agregar vínculo a Wikidata (sin cambios)
    if ccaa_clean in ccaa_wikidata_map:
        g.add((region_uri, OWL.sameAs, WIKIDATA[ccaa_wikidata_map[ccaa_clean]]))

    # URI de la observación (sin cambios)
    obs_uri = EX[f"{ccaa_clean}_{year}_{pol_clean}"]
    g.add((obs_uri, RDF.type, SCHEMA.Observation))
    g.add((obs_uri, SCHEMA.observedNode, region_uri))
    g.add((obs_uri, SCHEMA.observationDate, Literal(year, datatype=XSD.gYear)))

    # Medida y unidad
    if pol_clean in POLLUTANT_CONCEPT_MAP:

        g.add((obs_uri, SCHEMA.about, POLLUTANT_CONCEPT_MAP[pol_clean]))
        
        g.add((obs_uri, SCHEMA.value, Literal(float(value), datatype=XSD.float)))
        g.add((obs_uri, SCHEMA.unitCode, Literal(UNIT_MAP[pol_clean])))
    else:
        # Fallback (sin cambios)
        g.add((obs_uri, SCHEMA.value, Literal(float(value), datatype=XSD.float)))

# --- Guardar grafo ---
g.serialize(destination=OUTPUT_TTL, format='turtle')

print(f"Generado en:\n - {OUTPUT_TTL}")