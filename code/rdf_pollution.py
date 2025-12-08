import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD, OWL
import re

# --- Namespaces RDF ---
SCHEMA = Namespace("https://schema.org/")
BASE_URI = "https://csalas-alarcon.github.io/Grupo3_ADP/"
EX = Namespace(BASE_URI + "ontology/")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")

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

# --- Mapeo Contaminantes -> URI + unidades ---
UNIT_MAP = {
    "pm25": "UGM3",
    "pm10": "UGM3",
    "o3": "PPB",
    "no2": "PPB",
    "so2": "PPB",
    "co": "PPM"
}

PROPERTY_RESOURCES = {pol: EX[pol] for pol in UNIT_MAP.keys()}

# --- Rutas ---
INPUT_CSV = "../dist/kettle/pollution.csv"
OUTPUT_TTL = "../schema/total_pollution.ttl"
OUTPUT_RDF = "../schema/total_pollution.rdf"

# --- Leer CSV ---
df = pd.read_csv(INPUT_CSV, sep='\t')

# --- Crear grafo RDF ---
g = Graph()
g.bind("schema", SCHEMA)
g.bind("ex", EX)
g.bind("owl", OWL)

# --- Iterar sobre cada fila ---
for idx, row in df.iterrows():
    year = str(row["Year"])
    ccaa = str(row["CCAA"])
    pol = str(row["Type"])
    value = row["Value"]

    # Limpiar nombre para URI
    ccaa_clean = re.sub("_+", "_", ccaa.strip().replace(" ", "_"))
    pol_clean = re.sub("_+", "_", pol.strip().replace(" ", "_"))

    # URI del lugar
    region_uri = EX[f"Region_{ccaa_clean}"]
    g.add((region_uri, RDF.type, SCHEMA.Place))
    g.add((region_uri, SCHEMA.name, Literal(ccaa)))

    # Agregar vínculo a Wikidata si existe
    if ccaa_clean in ccaa_wikidata_map:
        g.add((region_uri, OWL.sameAs, WIKIDATA[ccaa_wikidata_map[ccaa_clean]]))

    # URI de la observación
    obs_uri = EX[f"{ccaa_clean}_{year}_{pol_clean}"]
    g.add((obs_uri, RDF.type, SCHEMA.Observation))
    g.add((obs_uri, SCHEMA.observedNode, region_uri))
    g.add((obs_uri, SCHEMA.observationDate, Literal(year, datatype=XSD.gYear)))

    # Medida y unidad
    if pol_clean in PROPERTY_RESOURCES:
        g.add((obs_uri, SCHEMA.measuredProperty, PROPERTY_RESOURCES[pol_clean]))
        g.add((obs_uri, SCHEMA.value, Literal(float(value), datatype=XSD.float)))
        g.add((obs_uri, SCHEMA.unitCode, Literal(UNIT_MAP[pol_clean])))
    else:
        # Por si hay alguna variable distinta a los contaminantes
        g.add((obs_uri, SCHEMA.value, Literal(float(value), datatype=XSD.float)))

# --- Guardar grafo ---
g.serialize(destination=OUTPUT_TTL, format='turtle')
g.serialize(destination=OUTPUT_RDF, format='xml')

print(f"Generated:\n - {OUTPUT_TTL}\n - {OUTPUT_RDF}")
