import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from rdflib.namespace import XSD
import re

# Namespaces RDF utilizados
SCHEMA = Namespace("https://schema.org/")
BASE_URI = "https://csalas-alarcon.github.io/Grupo3_ADP/"
EX = Namespace(BASE_URI + "ontology/")


# Rutas
INPUT_CSV = "../../dist/kettle/total_pollution.csv"
OUTPUT_TTL = "../../schema/total_pollution.ttl"
OUTPUT_RDF = "../../schema/total_pollution.rdf"

# Códigos de Unidades Estadarizados
UNIT_MAP = {
    "pm25": "UGM3",
    "pm10": "UGM3",
    "o3": "PPB",
    "no2": "PPB",
    "so2": "PPB",
    "co": "PPM"
}

# Recursos RDF
PROPERTY_RESOURCES = {
    "pm25": EX.PM25,
    "pm10": EX.PM10,
    "o3": EX.O3,
    "no2": EX.NO2,
    "so2": EX.SO2,
    "co": EX.CO
}

# Cargar CSV
df = pd.read_csv(INPUT_CSV, sep='\t')

# Grafo RDF
g = Graph()
g.bind("schema", SCHEMA)
g.bind("ex", EX)

# Convertimos filas en observaciones RDF
for idx, row in df.iterrows():
    year = str(row["date"])
    region_name = str(row["region"])

    # Limpiamos el nombre
    region_name_clean = re.sub("_+", "_", str(row["region"]).strip().replace(" ", "_"))
    region_name_original = str(row["region"]).strip()  # Keep original for label

    # URI para el recurso de la Región
    region_uri = EX[f"Region_{region_name_clean}"]

    # Creamos el recurso de la región.
    g.add((region_uri, RDF.type, SCHEMA.Place))
    g.add((region_uri, SCHEMA.name, Literal(region_name_original)))

    # Crear observación por contaminante
    for pol in PROPERTY_RESOURCES.keys():
        value = row[pol]

        # Nos saltamos valores erroneos
        if pd.isna(value):
            continue

        # Limpianos el nombre
        pol_clean = re.sub("_+", "_", str(pol).strip().replace(" ", "_"))

        # URI de la observación
        obs_uri = EX[f"{region_name_clean}_{year}_{pol_clean}"]

        # Añadimos triples RDF
        g.add((obs_uri, RDF.type, SCHEMA.Observation))
        g.add((obs_uri, SCHEMA.observedNode, region_uri))
        g.add((obs_uri, SCHEMA.observationDate, Literal(year, datatype=XSD.gYear)))
        g.add((obs_uri, SCHEMA.measuredProperty, PROPERTY_RESOURCES[pol]))
        g.add((obs_uri, SCHEMA.value, Literal(float(value), datatype=XSD.float)))
        g.add((obs_uri, SCHEMA.unitCode, Literal(UNIT_MAP[pol])))



# Guardar como Turtle
g.serialize(destination=OUTPUT_TTL, format='turtle')

# Guardar como RDF/XML
g.serialize(destination=OUTPUT_RDF, format='xml')

print(f"Generated:\n - {OUTPUT_TTL}\n - {OUTPUT_RDF}")
