# <=====================================================================>

#   ███████╗██╗  ██╗████████╗███████╗███╗   ██╗██████╗ ███████╗██████╗
#   ██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗
#   █████╗   ╚███╔╝    ██║   █████╗  ██╔██╗ ██║██║  ██║█████╗  ██║  ██║
#   ██╔══╝   ██╔██╗    ██║   ██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██║  ██║
#   ███████╗██╔╝ ██╗   ██║   ███████╗██║ ╚████║██████╔╝███████╗██████╔╝
#   ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═════╝

# <=====================================================================>
#             Create maps with data extended with Wikidata
# <=====================================================================>
#  Imports:
# <=====================================================================>
from rdflib import Graph, Namespace
import plotly.express as px
import urllib.request
import pandas as pd
import json
import sys
import os
# <=====================================================================>
#  Configuration & Constants:
# <=====================================================================>
#  Script working directory
# <=====================================================================>
WKDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
# <=====================================================================>
#  Input Schema directory (TTL files)
# <=====================================================================>
SCHEMA_DIR = WKDIR + '/../../schema'
# <=====================================================================>
#  Output directory for maps
# <=====================================================================>
OUTDIR = WKDIR + '/../extended/'
# <=====================================================================>
#  GeoJSON URL for Spain's CCAA
# <=====================================================================>
GEOJSON_URL = 'https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson'
# <=====================================================================>
#  Namespaces
# <=====================================================================>
SCHEMA = Namespace('http://schema.org/')
# <=====================================================================>
OWL = Namespace('http://www.w3.org/2002/07/owl#')
# <=====================================================================>
#  Maps:
# <=====================================================================>
#  WikidataID to GeoJSON Name
# <=====================================================================>
WIKIDATA_TO_GEOJSON = {
    'Q5718': 'Andalucia',          # GeoJSON: Sin tilde
    'Q4040': 'Aragon',             # GeoJSON: Sin tilde
    'Q3934': 'Asturias',           # GeoJSON: Nombre corto
    'Q4071': 'Baleares',           # GeoJSON: Nombre corto
    'Q5709': 'Canarias',           # GeoJSON: Coincide
    'Q3946': 'Cantabria',          # GeoJSON: Coincide
    'Q5748': 'Castilla-La Mancha', # GeoJSON: Coincide
    'Q5739': 'Castilla-Leon',      # GeoJSON: Sin 'y' y sin tilde
    'Q5705': 'Cataluña',           # GeoJSON: Coincide
    'Q5720': 'Valencia',           # GeoJSON: Nombre corto
    'Q5777': 'Extremadura',        # GeoJSON: Coincide
    'Q3911': 'Galicia',            # GeoJSON: Coincide
    'Q5727': 'La Rioja',           # GeoJSON: Coincide
    'Q5756': 'Madrid',             # GeoJSON: Nombre corto
    'Q5768': 'Murcia',             # GeoJSON: Nombre corto
    'Q4018': 'Navarra',            # GeoJSON: Nombre corto
    'Q3995': 'Pais Vasco',         # GeoJSON: Sin tilde
    'Q5823': 'Ceuta',              # GeoJSON: Coincide
    'Q5831': 'Melilla'             # GeoJSON: Coincide
}
# <=====================================================================>
#  Functions:
# <=====================================================================>
#  Ensure directory exists
# <=====================================================================>
def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)
# <=====================================================================>
#  Download GeoJSON geometry
# <=====================================================================>
def get_geojson():
    print(f' -> Downloading CCAA geometries from: {GEOJSON_URL}...')
    try:
        with urllib.request.urlopen(GEOJSON_URL) as url:
            return json.loads(url.read().decode())
    except Exception as e:
        print(f'Error downloading GeoJSON: {e}')
        return None
# <=====================================================================>
#  Code:
# <=====================================================================>
#  Initialize output directory
# <=====================================================================>
ensure_dir(OUTDIR)
# <=====================================================================>
#  Initialize graph
# <=====================================================================>
g = Graph()
# <=====================================================================>
#  Load all .ttl files from schema directory
# <=====================================================================>
print(f'Loading RDF files from {os.path.abspath(SCHEMA_DIR)}...')
# <=====================================================================>
files = [f for f in os.listdir(SCHEMA_DIR) if f.endswith('.ttl')]
# <=====================================================================>
if not files:
    print('Error loading files: No .ttl files found')
    sys.exit(1)
# <=====================================================================>
#  Loop trough files
# <=====================================================================>
for file in files:
    try:
        g.parse(os.path.join(SCHEMA_DIR, file), format='turtle')
        print(f'  + Loaded: {file}')
    except Exception as e:
        print(f'  - Error in: {file} -> {e}')
# <=====================================================================>
#  Extract Data from Local Graph (SPARQL)
# <=====================================================================>
print('Extracting local data with SPARQL...')
# <=====================================================================>
results = g.query('''
    PREFIX schema: <http://schema.org/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?var ?year ?val ?wd_uri WHERE {
        ?obs a schema:Observation ;
             schema:variableMeasured ?var ;
             schema:value ?val ;
             schema:observationDate ?year ;
             schema:areaServed ?place .
        ?place owl:sameAs ?wd_uri .
    }
''')
# <=====================================================================>
#  Transform results to Pandas DataFrame
# <=====================================================================>
data = []
for result in results:
    data.append({
        'Value': float(result.val),
        'Variable': str(result.var),
        'Year': int(str(result.year)),
        'WikidataID': str(result.wd_uri).split('/')[-1]
    })
# <=====================================================================>
df = pd.DataFrame(data)
# <=====================================================================>
if df.empty:
    print('Error with dataframe: Dataframe empty')
    sys.exit(1)
# <=====================================================================>
#  Remove 'total nacional' entries
# <=====================================================================>
df = df[df['WikidataID'] != 'Q29']
# <=====================================================================>
#  Get GeoJSON data
# <=====================================================================>
geojson = get_geojson()
if not geojson: sys.exit(1)
# <=====================================================================>
#  Merge mapped names into DataFrame
# <=====================================================================>
df['GeoName'] = df['WikidataID'].map(WIKIDATA_TO_GEOJSON)
# <=====================================================================>
missing = df[df['GeoName'].isna()]
if not missing.empty:
    print(f' [WARNING] There are still {len(missing)} rows without geographical mapping. IDs: {missing['WikidataID'].unique()}')
else:
    print(' [OK] Geographical coverage correct')
# <=====================================================================>
#  Generate all maps
# <=====================================================================>
variables = df['Variable'].unique()
print(f'Generating maps for {len(variables)} variables...')
# <=====================================================================>
for var in variables:
    # <=====================================================================>
    #  Filter data for current variable
    # <=====================================================================>
    df_sub = df[df['Variable'] == var].sort_values('Year')
    if df_sub.empty: continue
    # <=====================================================================>
    #  Create Choropleth Mapbox
    # <=====================================================================>
    print(f' -> Mapping: {var}')
    # <=====================================================================>
    min_v = df_sub['Value'].min()
    max_v = df_sub['Value'].max()
    # <=====================================================================>
    fig = px.choropleth_map(
        df_sub,
        zoom = 5,
        opacity = 0.85,
        color = 'Value',
        geojson = geojson,
        locations = 'GeoName',
        title = f'Mapa: {var}',
        animation_frame = 'Year',
        template = 'plotly_dark',
        range_color = (min_v, max_v),
        featureidkey = 'properties.name',
        map_style = 'carto-darkmatter',
        color_continuous_scale = 'Viridis',
        center = {'lat': 40.4168, 'lon': -3.7038}
    )
    # <=====================================================================>
    #  Adjust map layout
    # <=====================================================================>
    fig.update_layout(
        margin = {'r': 0, 't': 50, 'l': 0, 'b': 0},
        paper_bgcolor = '#000000',
        plot_bgcolor = '#000000',
        font_color = 'white',
        title_x = 0.05,
        title_y = 0.95
    )
    # <=====================================================================>
    #  Save map to HTML file
    # <=====================================================================>
    var_escaped = var.replace(' ', '_').replace('/', '_').lower()
    outfile = os.path.join(OUTDIR, f'map_{var_escaped}.html')
    try:
        fig.write_html(outfile)
        print(f'    Saved: {outfile}')
    except Exception as e:
        print(f'    Error when saving: {e}')
# <=====================================================================>
#  End of Script
# <=====================================================================>
print('Successfully finished script!')
# <=====================================================================>
