import os  

BASE_URI = "https://github.com/csalas-alarcon/Grupo3_ADP/"


enlaces_wikidata = {
    "andalucia": "http://www.wikidata.org/entity/Q5718",
    "aragon": "http://www.wikidata.org/entity/Q4040",
    "asturias": "http://www.wikidata.org/entity/Q3934",
    "baleares": "http://www.wikidata.org/entity/Q5720",
    "canarias": "http://www.wikidata.org/entity/Q5783", 
    "cantabria": "http://www.wikidata.org/entity/Q3946",
    "castilla_la_mancha": "http://www.wikidata.org/entity/Q5748",
    "castilla_leon": "http://www.wikidata.org/entity/Q5739",
    "catalunya": "http://www.wikidata.org/entity/Q5705", 
    "ceuta": "http://www.wikidata.org/entity/Q5823",
    "comunidad_valenciana": "http://www.wikidata.org/entity/Q5724",
    "extremadura": "http://www.wikidata.org/entity/Q5777",
    "galicia": "http://www.wikidata.org/entity/Q3911",
    "rioja": "http://www.wikidata.org/entity/Q5727",
    "madrid": "http://www.wikidata.org/entity/Q5756",
    "melilla": "http://www.wikidata.org/entity/Q5831",
    "murcia": "http://www.wikidata.org/entity/Q5710",
    "navarra": "http://www.wikidata.org/entity/Q4018",
    "pais_vasco": "http://www.wikidata.org/entity/Q3995",
    "total_nacional":"http://www.wikidata.org/entity/Q29",
    "total": "http://www.wikidata.org/entity/Q29",
    "nacional":"http://www.wikidata.org/entity/Q29"
}

ttl_content = f"""@prefix ex: <{BASE_URI}> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""

for region, wikidata_url in enlaces_wikidata.items():
    # Tripleta: MiRegion -> es igual a -> WikidataRegion
    ttl_content += f"ex:Region_{region} owl:sameAs <{wikidata_url}> .\n"
    # Añadimos una etiqueta legible también
    ttl_content += f'ex:Region_{region} rdfs:label "{region.replace("_", " ").title()}" .\n'

# GUARDAR EN LA CARPETA 'archivos_ttl'
carpeta_salida = "archivos_ttl"

if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

nombre_archivo = "enlaces_wikidata.ttl"
ruta_completa = os.path.join(carpeta_salida, nombre_archivo)

with open(ruta_completa, "w", encoding="utf-8") as f:
    f.write(ttl_content)

print(f"¡Archivo de enriquecimiento guardado en: {ruta_completa}!")