import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from rdflib.namespace import XSD

# -----------------------------
# Namespaces
# -----------------------------
SCHEMA = Namespace("https://schema.org/")
EX = Namespace("http://example.org/pollution/")

# -----------------------------
# Input / Output
# -----------------------------
INPUT_CSV = "../../dist/kettle/pollution/total_pollution.csv"
OUTPUT_TTL = "../../schema/total_pollution.ttl"
OUTPUT_RDF = "../../schema/total_pollution.rdf"

# -----------------------------
# Unit codes (confirmed)
# -----------------------------
UNIT_MAP = {
    "pm25": "UGM3",
    "pm10": "UGM3",
    "o3": "PPB",
    "no2": "PPB",
    "so2": "PPB",
    "co": "PPM"
}

# -----------------------------
# Pollutants mapping -> resource names
# -----------------------------
PROPERTY_RESOURCES = {
    "pm25": EX.PM25,
    "pm10": EX.PM10,
    "o3": EX.O3,
    "no2": EX.NO2,
    "so2": EX.SO2,
    "co": EX.CO
}

# -----------------------------
# Load CSV
# -----------------------------
df = pd.read_csv(INPUT_CSV, sep=';')

# -----------------------------
# RDF Graph
# -----------------------------
g = Graph()
g.bind("schema", SCHEMA)
g.bind("ex", EX)

# -----------------------------
# Convert rows into Observations
# -----------------------------
for idx, row in df.iterrows():
    year = str(row["date"])
    region_name = str(row["region"])

    # URI for the region (as a resource)
    region_uri = EX[f"Region_{region_name}"]

    # Create region resource (optional, but useful)
    g.add((region_uri, RDF.type, SCHEMA.Place))
    g.add((region_uri, SCHEMA.name, Literal(region_name)))

    # For each pollutant, create an Observation
    for pol in PROPERTY_RESOURCES.keys():
        value = row[pol]

        # Skip missing values just in case (should not happen)
        if pd.isna(value):
            continue

        obs_uri = EX[f"{region_name}_{year}_{pol}"]

        g.add((obs_uri, RDF.type, SCHEMA.Observation))
        g.add((obs_uri, SCHEMA.observedNode, region_uri))
        g.add((obs_uri, SCHEMA.observationDate, Literal(year, datatype=XSD.gYear)))
        g.add((obs_uri, SCHEMA.measuredProperty, PROPERTY_RESOURCES[pol]))
        g.add((obs_uri, SCHEMA.value, Literal(float(value), datatype=XSD.float)))
        g.add((obs_uri, SCHEMA.unitCode, Literal(UNIT_MAP[pol])))

# -----------------------------
# Save to Turtle
# -----------------------------
g.serialize(destination=OUTPUT_TTL, format='turtle')

# -----------------------------
# Save to RDF/XML
# -----------------------------
g.serialize(destination=OUTPUT_RDF, format='xml')

print(f"Generated:\n - {OUTPUT_TTL}\n - {OUTPUT_RDF}")
