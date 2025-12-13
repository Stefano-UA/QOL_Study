# <=================================================================================>

#   ████████╗██████╗  █████╗ ███████╗███╗   ██╗███████╗ ██████╗ ██████╗ ███╗   ███╗
#   ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██╔═══██╗██╔══██╗████╗ ████║
#      ██║   ██████╔╝███████║███████╗██╔██╗ ██║█████╗  ██║   ██║██████╔╝██╔████╔██║
#      ██║   ██╔══██╗██╔══██║╚════██║██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║
#      ██║   ██║  ██║██║  ██║███████║██║ ╚████║██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║
#      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝

# <=================================================================================>
#          Transforms data from CSVs into a normalized RDF Knowledge Graph
# <=================================================================================>
#  Imports:
# <=================================================================================>
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD
import pandas as pd
import sys
import os
# <=================================================================================>
#  Configuration & Constants:
# <=================================================================================>
#  Script working directory
# <=================================================================================>
WKDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
# <=================================================================================>
#  Input data directory to use
# <=================================================================================>
DATADIR = WKDIR + '/../../dist/kettle/'
# <=================================================================================>
#  Output directory for transformations
# <=================================================================================>
OUTDIR = WKDIR + '/../'
# <=================================================================================>
#  Processing Config:
# <=================================================================================>
from processing import config as fconfig
# <=================================================================================>
#  Namespaces:
# <=================================================================================>
#  Our own namespace
# <=================================================================================>
EX = Namespace('https://csalas-alarcon.github.io/Grupo3_ADP/ontology/')
# <=================================================================================>
#  CHEBI namespace -> http://purl.obolibrary.org
# <=================================================================================>
CHEBI = Namespace('http://purl.obolibrary.org/obo/CHEBI_')
# <=================================================================================>
#  ENVO namespace -> http://purl.obolibrary.org
# <=================================================================================>
ENVO = Namespace('http://purl.obolibrary.org/obo/ENVO_')
# <=================================================================================>
#  ECTO namespace -> http://purl.obolibrary.org
# <=================================================================================>
ECTO = Namespace('http://purl.obolibrary.org/obo/ECTO_')
# <=================================================================================>
#  LFID namespace -> http://purl.obolibrary.org
# <=================================================================================>
LFID = Namespace('http://purl.obolibrary.org/obo/LFID_')
# <=================================================================================>
#  Wikidata namespace -> http://www.wikidata.org
# <=================================================================================>
WIKIDATA = Namespace('http://www.wikidata.org/entity/')
# <=================================================================================>
#  OWL namespace -> http://www.w3.org
# <=================================================================================>
OWL = Namespace('http://www.w3.org/2002/07/owl#')
# <=================================================================================>
#  Schema namespace -> http://schema.org
# <=================================================================================>
SCHEMA = Namespace('http://schema.org/')
# <=================================================================================>
#  Maps:
# <=================================================================================>
#  WIKIDATA CCAA to ID map
# <=================================================================================>
CCAA_TO_WIKIDATA = {
    'andalucia': 'Q5718', 'aragon': 'Q4040', 'asturias': 'Q3934',
    'baleares': 'Q4071', 'canarias': 'Q5709', 'cantabria': 'Q3946',
    'castilla_la_mancha': 'Q5748', 'castilla_leon': 'Q5739',
    'catalunya': 'Q5705', 'ceuta': 'Q5823', 'comunidad_valenciana': 'Q5720',
    'extremadura': 'Q5777', 'galicia': 'Q3911', 'la_rioja': 'Q5727',
    'madrid': 'Q5756', 'melilla': 'Q5831', 'murcia': 'Q5768',
    'navarra': 'Q4018', 'pais_vasco': 'Q3995', 'rioja': 'Q5727',
    'total_nacional': 'Q29', 'spain': 'Q29', 'españa': 'Q29'
}
# <=================================================================================>
#  UNIT to TYPE map
# <=================================================================================>
UNIT_TO_TYPE = {
    'co': LFID['0000786'],
    'o3': ECTO['9000052'],
    'no2': LFID['0000787'],
    'so2': LFID['0000793'],
    'pm25': LFID['0000795'],
    'pm10': LFID['0000795'],
    'gini': LFID['0001254'],
    'desigualdad_(s80/s20)': LFID['0001254'],
    'renta_neta_media_por_persona': LFID['0001116'],
    'renta_media_por_unidad_de_consumo': LFID['0001244']
}
# <=================================================================================>
#  UNIT to OBJECT map
# <=================================================================================>
UNIT_TO_OBJECT = {
    'pm25': ENVO['01003002'],
    'pm10': ENVO['01003002'],
    'o3': CHEBI['25812'],
    'no2': CHEBI['29424'],
    'so2': CHEBI['29820'],
    'co': CHEBI['17245']
}
# <=================================================================================>
#  Code:
# <=================================================================================>
#  Function to do the transformaton for a config
# <=================================================================================>
def transform(config):
    # Get CSV path
    csv_path = os.path.join(DATADIR, config['infile'])
    # Check existence
    if not os.path.exists(csv_path):
        print(f'NOT FOUND: {csv_path}')
        return

    print(f'Processing {os.path.abspath(csv_path)}...')

    try:
        # Automatically detect separator
        df = pd.read_csv(csv_path, sep=None, engine='python')
    except Exception as e:
        print(f'Error reading {config['infile']}: {e}')
        return

    # Make graph
    g = Graph()
    g.bind('ex', EX)
    g.bind('owl', OWL)
    g.bind('ecto', ECTO)
    g.bind('lfid', LFID)
    g.bind('schema', SCHEMA)
    if 'pollution' in config:
        g.bind('envo', ENVO)
        g.bind('chebi', CHEBI)

    # Loop trough CSV
    for index,row in df.iterrows():
        try:
            row_type = None
            # Check mappings
            if 'mappings' in config:
                # Get data type
                row_type = row.get('Type')
                # If we dont handle the type we ignore it
                if row_type not in config['mappings']:
                    continue

            # Get relevant properties
            slug = config['mappings'][row_type]['slug'] if row_type else config['slug']
            unit = config['mappings'][row_type]['unit'] if row_type else config['unit']
            label = config['mappings'][row_type]['label'] if row_type else config['label']

            try:
                # Get relevant data
                y,  ca, v = row['Year'], row['CCAA'], row['Value']
                # Check for total values
                if 'total' in ca:
                    ca = 'españa'
            except:
                # Skip if any data is not present
                continue

            # Do PLACE
            uri_place = EX[f'Region_{ca}']
            g.add((uri_place, RDF.type, SCHEMA.Place))
            g.add((uri_place, SCHEMA.name, Literal(ca)))
            g.add((uri_place, SCHEMA.containedInPlace, WIKIDATA[CCAA_TO_WIKIDATA['spain']]))
            # Set sameAs with wikidata if present
            if ca in CCAA_TO_WIKIDATA:
                g.add((uri_place, OWL.sameAs, WIKIDATA[CCAA_TO_WIKIDATA[ca]]))
                g.add((uri_place, SCHEMA.sameAs, WIKIDATA[CCAA_TO_WIKIDATA[ca]]))

            # Do DATASET -> Year
            uri_dataset_year = EX[f'Dataset/Year_{y}']
            g.add((uri_dataset_year, RDF.type, SCHEMA.Dataset))
            g.add((uri_dataset_year, SCHEMA.name, Literal(f'Datos Año {y}')))
            g.add((uri_dataset_year, SCHEMA.variableMeasured, Literal(label)))
            g.add((uri_dataset_year, SCHEMA.temporalCoverage, Literal(y, datatype=XSD.gYear)))

            # Do DATASET -> Region
            uri_dataset_region = EX[f'Dataset/Region_{ca.capitalize()}']
            g.add((uri_dataset_region, RDF.type, SCHEMA.Dataset))
            g.add((uri_dataset_region, SCHEMA.variableMeasured, Literal(label)))
            g.add((uri_dataset_region, SCHEMA.name, Literal(f'Datos Históricos {ca}')))
            g.add((uri_dataset_region, SCHEMA.spatialCoverage, uri_place))

            # Do OBSERVATION
            uri_obs = EX[f'Observation/{slug}_{ca}_{y}']
            g.add((uri_obs, RDF.type, SCHEMA.Observation))
            g.add((uri_obs, SCHEMA.areaServed, uri_place))
            g.add((uri_obs, SCHEMA.unitText, Literal(unit)))
            g.add((uri_obs, SCHEMA.isPartOf, uri_dataset_year))
            g.add((uri_obs, SCHEMA.observationAbout, uri_place))
            g.add((uri_obs, SCHEMA.isPartOf, uri_dataset_region))
            g.add((uri_obs, SCHEMA.variableMeasured, Literal(label)))
            g.add((uri_obs, SCHEMA.observationPeriod, Literal('P1Y'))) # 1 Year
            g.add((uri_obs, SCHEMA.value, Literal(v, datatype=XSD.float)))
            g.add((uri_obs, SCHEMA.observationDate, Literal(y, datatype=XSD.gYear)))
            if row_type in UNIT_TO_TYPE:
                g.add((uri_obs, SCHEMA.additionalType, UNIT_TO_TYPE[row_type]))
            if row_type in UNIT_TO_OBJECT:
                g.add((uri_obs, SCHEMA.additionalType, UNIT_TO_OBJECT[row_type]))

        except Exception as e:
            print(e)
            continue

    # Save to file
    os.makedirs(OUTDIR, exist_ok=True)
    g.serialize(destination=os.path.join(OUTDIR, config['outfile']), format='turtle')
    print(f' -> Generated: {config['outfile']} ({len(g)} triplets)')
# <=================================================================================>
#  What to run when called as a script
# <=================================================================================>
if (__name__ == '__main__'):
    print(f'Looking for files in {os.path.abspath(DATADIR)}...')
    # Loop through files to process
    for entry in fconfig:
        transform(entry)
