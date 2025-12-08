# Adquisición y Preparación de Datos (G3)

## Equipo

- Carlos Salas - [Gh](https://github.com/csalas-alarcon)
- David Muñoz - [Gh](https://github.com/oppangangnamsta)
- Linxi Jiang - [Gh](https://github.com/Linxi-Jiang)
- Stefano Bia - [Gh](https://github.com/Stefano-UA)

## Apartados

1. - [X] Temática y Preguntas
2. - [X] Obtención de Datos
3. - [ ] Diseño Conceptual, Lógico y Físico
4. - [ ] Extracción y Preparación de Datos (pentaho)
5. - [ ] Transformación de Datos (tripletas)
6. - [ ] Visualizaciones
7. - [ ] Memoria del Trabajo
8. - [ ] Repositorio GitHub

### Revisiones

Aqui tenemos indicadas las revisiones realizadas para cada apartado por cada miembro del equipo.
Las casillas **marcadas** con una *X* indican que ese miembro del equipo le ha dado su **visto bueno** a ese apartado.

| Apartado | Salas | David | Linxi | Stefano |
|:-:|:---:|:---:|:---:|:---:|
| 1 | (X) | (X) | (X) | (X) |
| 2 | ( ) | ( ) | ( ) | (X) |
| 3 | ( ) | ( ) | ( ) | ( ) |
| 4 | ( ) | ( ) | ( ) | (X) |
| 5 | ( ) | ( ) | ( ) | ( ) |
| 6 | ( ) | ( ) | ( ) | (X) |
| 7 | ( ) | ( ) | ( ) | ( ) |
| 8 | ( ) | ( ) | ( ) | ( ) |

## Estructura del Repositorio

- ./**data**: Datos obtenidos
    - /**pollution**: Datos de sensores de contaminación por CCAA
    - /*gini_ccaa.csv*: Índice de desigualdad GINI por CCAA
    - /*ipc_ccaa.csv*: Índice de Precios de Consumo por CCAA
    - /*pibc_ccaa.csv*: Producto Interior Bruto per capita por CCAA
    - /*pob_ccaa.csv*: Cantidad de población por CCAA
    - /*qol_ccaa.xslx*: Indice de calidad de vida por CCAA
    - /*qol_ccaa_ex.xslx*: Indice de calidad de vida por CCAA con muchos datos extra
- ./**design**: Diseños del almacen de datos
    - /*conceptual.md*: Diseño conceptual
    - /*logic.png*: Diseño lógico
    - /*logic.mwb*: Diseño lógico, modelo de MySQL Workbench
    - /*physic.sql*: Diseño físico
- ./**dist**: Agregados de datos final
    - /**kettle**: Agregados generados por las transformaciones de Pentaho y Python
    - /*data.csv*: Agregado de datos final
- ./**docs**: Documentación del trabajo
    - /*Memoria.pdf*: Memoria del trabajo (versión final)
    - /*Memoria.odt*: Memoria del trabajo
- ./**kettle**: Trabajos y transformaciones
    - /**pollution**: Trabajos y transformaciones de pollution hechos en Python
    - /**steps**: Transformaciones de Pentaho para cada uno de los CSV de entrada
    - /*agg_all.ktr*: Transformación de Pentaho para agregar todos los CSV limpios en uno final
    - /*data.kjb*: Trabajo de Pentaho que orquestra todo el proceso de limpieza, transformación y agregación de datos
- ./**schema**: Modelos Semánticos
    - /*.ttl*:
    - /*.rdf*:
- ./**visuals**: Visualizaciones de datos
    - /**code**: Código para generar las visualizaciones
    - /*.png*: Visualizaciones

## Preguntas a Responder

- ¿Cómo influye la economia de una CCAA en la calidad de vida de sus habitantes?
- ¿Cómo influyen el turismo y la contaminación de una CCAA en la calidad de vida de sus habitantes?
- ¿Influye más la economia de la CCAA o su turismo y contaminación en la calidad de vida de sus habitantes?

## Datos Relevantes

Haremos uso de los siguientes datos para tratar de responder a estas preguntas.
Los datos agregaran la información por **Año**, fijandonos a poder ser en los más *recientes*,
por **CCAA** y sin tener en cuenta el **Sexo** de las personas.

- Contaminación del aire -> *pollution/*
- Cantidad de población -> *pob_ccaa.csv*
- Indice de calidad de vida -> *qol_ccaa.xslx*
- Índice de precios de consumo -> *ipc_ccaa.csv*
- Producto interior bruto per capita -> *pibc_ccaa.csv*
- Índice de desigualdad económica GINI -> *gini_ccaa.csv*

## Agregación de Datos

La agregación de datos la realizaremos basandonos en las siguientes columnas.
Estas columnas deben tener **exactamente** el nombre indicado y sus valores tienen que estar **formateados** como se indica.

### Year

Contiene el año en formato YYYY como valor. Ej. 2025.

### CCAA

Contiene una de las siguientes Comunidades Autónomas como valor:

- total_nacional
- andalucia
- aragon
- asturias
- baleares
- canarias
- cantabria
- castilla_leon
- castilla_la_mancha
- catalunya
- ceuta
- comunidad_valenciana
- extremadura
- galicia
- la_rioja
- madrid
- mellila
- murcia
- navarra
- pais_vasco

## Limpieza General de Datos

A la hora de procesar los datos, con las transformaciones de pentaho,
realizaremos las siguientes operaciones de limpieza, en orden.

### String operations

- *Trim type*: **both** -> Quita los espacios sobrantes al principio y al final de la cadena.
- *Lower/Upper*: **lower** -> Normaliza todos los caracteres a minusculas.
- *Remove Sepcial Character*: **carriage return & line feed** -> Quita los caracteres especiales *\cr* y *\n*.

### Replace in string

Reemplazaremos ciertos caracteres con otros siguiendo:

| Reemplazar | Remplazo |
|:-----:|:--:|
| à o á | a |
| è o é | e |
| ì o í | i |
| ò o ó | o |
| ù o ú | u |
| ñ | ny |
| '&nbsp;' | _ |

### Other

Todo lo demás que tengamos que hacer con los datos.

### Number Format

Los valores numéricos también deben seguir un formato.
En nuestro caso simplemente se usará la coma como separador decimal y no se usaran puntos para nada.

### Sort rows

Finalmente, ordenaremos los datos por las siguientes columnas:

1. [**Ascendente**] Year
2. [**Ascendente**] CCAA

## Visualizaciones

Finalmente tenemos las visualizaciones de los datos agregados (data.csv).

### PIB vs QOL

![PIB vs QOL](./visuals/pib_vs_qol.png)

Esta gráfica revela una correlación lineal positiva robusta entre la potencia económica y el bienestar, donde las rectas de regresión confirman que un mayor PIB per cápita es un predictor fiable de una mejor calidad de vida. Se observa una divergencia interesante entre las mediciones nominales y las ajustadas por unidad de consumo en los tramos altos del eje X; esto indica que, en las regiones más ricas, el coste de vida actúa como un factor de corrección que reduce el poder adquisitivo real, sugiriendo que el crecimiento nominal sobreestima ligeramente la mejora en el bienestar si no se descuenta la inflación.

### POLL vs QOL

![POLL vs QOL](./visuals/poll_vs_qol.png)

El análisis normalizado muestra una tendencia estructural negativa, indicando que la masificación demográfica y la degradación ambiental actúan como penalizadores directos del bienestar. Las pendientes descendentes de las regresiones sugieren que a medida que una comunidad se desvía por encima de la media en población o contaminación (avanzando en el eje Z-Score), su índice de calidad de vida decae, observándose que la concentración demográfica tiene una pendiente negativa ligeramente más pronunciada que la contaminación por sí sola, lo que implica que el estrés urbano podría ser un factor más determinante que la calidad del aire aislada.

### GINI vs QOL

![GINI vs QOL](./visuals/gini_vs_qol.png)

Esta visualización presenta la relación inversa más clara y determinista de todo el conjunto de datos, caracterizada por una pendiente negativa pronunciada y una dispersión relativamente baja alrededor de la recta de regresión. Los datos indican que la desigualdad social es un cuello de botella crítico para el desarrollo; independientemente de otros factores, un índice GINI elevado castiga drásticamente la calidad de vida, lo que matemáticamente posiciona  a la equidad como un requisito previo estadístico más fuerte para el bienestar que el propio volumen económico.

### IPC vs QOL

![IPC vs QOL](./visuals/ipc_vs_qol.png)

La representación expone la nula capacidad predictiva del IPC respecto al bienestar general, evidenciada por una recta de regresión prácticamente horizontal y una nube de puntos dispersa sin patrón aparente. Esto implica que el coste de vida es una variable de contexto sin impacto directo en la ecuación de calidad de vida en este modelo, probablemente porque los salarios y servicios se ajustan a los precios locales, neutralizando cualquier ventaja o desventaja inherente a ser una región "cara" o "barata".

### Trade-Offs

![Trade-Offs](./visuals/trade_offs.png)

Este gráfico de perfiles multivariables visualiza la optimización de objetivos contrapuestos, mostrando que las regiones con mejor desempeño no solo maximizan el eje económico, sino que logran minimizar simultáneamente la desigualdad y la contaminación. Se aprecian cruces en forma de tijera entre las líneas de alto y bajo rendimiento, lo que demuestra que existe un compromiso estructural o trade-off: el éxito en calidad de vida no proviene de saturar una sola dimensión, sino de mantener el PIB alto mientras se fuerzan las variables de coste social y ambiental hacia los mínimos del eje normalizado.

### Correlation Heatmap

![Correlation Heatmap](./visuals/heatmap.png)

La matriz sintetiza el peso cuantitativo de las variables, confirmando mediante los coeficientes Beta estandarizados que la desigualdad (GINI) es el vector con mayor magnitud de impacto, superando incluso a los indicadores económicos. Mientras que el PIB ejerce una tracción positiva significativa, los coeficientes negativos de la contaminación y la desigualdad revelan que el modelo de calidad de vida es más sensible a los detractores sociales y ambientales que a los incrementos puramente macroeconómicos, validando matemáticamente las tendencias observadas en los gráficos de dispersión.

## Last Edited

- 8/12/25 - Stefano
- 5/12/25 - Carlos
