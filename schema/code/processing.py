# <=================================================================================>

#   ██████╗ ██████╗  ██████╗  ██████╗███████╗███████╗███████╗██╗███╗   ██╗ ██████╗
#   ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔════╝██║████╗  ██║██╔════╝
#   ██████╔╝██████╔╝██║   ██║██║     █████╗  ███████╗███████╗██║██╔██╗ ██║██║  ███╗
#   ██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝  ╚════██║╚════██║██║██║╚██╗██║██║   ██║
#   ██║     ██║  ██║╚██████╔╝╚██████╗███████╗███████║███████║██║██║ ╚████║╚██████╔╝
#   ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝

# <=================================================================================>
#                         Configuration of files to process
# <=================================================================================>
config = (
    { # 1. GINI
        'infile': 'gini_ccaa.csv',
        'outfile': 'rdf_gini.ttl',
        'mappings': {
            'gini': { 'slug': 'gini', 'label': 'Indice GINI', 'unit': 'Index' },
            'desigualdad_(s80/s20)': { 'slug': 's80_s20', 'label': 'Ratio S80/S20', 'unit': 'Ratio' }
        }
    },
    { # 2. IPC
        'infile': 'ipca_ccaa.csv',
        'outfile': 'rdf_ipca.ttl',
        'mappings': {
            'indice': { 'slug': 'ipc_indice', 'label': 'Indice de Precios de Consumo', 'unit': 'Index' },
            'variacion_anual': { 'slug': 'ipc_var', 'label': 'Variacion Anual del IPC', 'unit': 'Percentage' }
        }
    },
    { # 3. PIB
        'infile': 'pibc_ccaa.csv',
        'outfile': 'rdf_pibc.ttl',
        'mappings': {
            'renta_neta_media_por_persona': { 'slug': 'renta_persona', 'label': 'Renta Neta Media por Persona', 'unit': 'Euro' },
            'renta_media_por_unidad_de_consumo': { 'slug': 'renta_unidad_consumo', 'label': 'Renta Media por Unidad Consumo', 'unit': 'Euro' }
        }
    },
    { # 4. POBLACIÓN
        'infile': 'pob_ccaa.csv',
        'outfile': 'rdf_pob.ttl',
        'slug': 'poblacion', 'label': 'Poblacion Total', 'unit': 'Personas'
    },
    { # 5. CALIDAD DE VIDA
        'infile': 'qol_ccaa.csv',
        'outfile': 'rdf_qol.ttl',
        'slug': 'calidad_vida', 'label': 'Indice Calidad de Vida', 'unit': 'Index'
    },
    { # 6. CONTAMINACIÓN
        'pollution': True,
        'infile': 'pollution.csv',
        'outfile': 'rdf_poll.ttl',
        'mappings': {
            'o3': { 'slug': 'o3_en_aire', 'label': 'Ozono', 'unit': 'PPB' },
            'co': { 'slug': 'co_en_aire', 'label': 'Monoxido de Carbono', 'unit': 'PPB' },
            'no2': { 'slug': 'no2_en_aire', 'label': 'Dioxido de Nitrogeno', 'unit': 'PPB' },
            'so2': { 'slug': 'so2_en_aire', 'label': 'Dioxido de Azufre', 'unit': 'PPB' },
            'pm10': { 'slug': 'pm10_en_aire', 'label': 'Particulas Menores de 10 Micras', 'unit': 'UGM3' },
            'pm25': { 'slug': 'pm25_en_aire', 'label': 'Particulas Menores de 2.5 Micras', 'unit': 'UGM3' }
        }
    }
)
# <=================================================================================>