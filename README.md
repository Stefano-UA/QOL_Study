# Adquisición y Preparación de Datos (G3)

## Equipo

- Carlos Salas - [Gh](https://github.com/csalas-alarcon)
- David Muñoz - [Gh](https://github.com)
- Linxi Jiang - [Gh](https://github.com/Linxi-Jiang)
- Stefano Bia - [Gh](https://github.com/Stefano-UA)

## Apartados

1. - [X] Temática y Preguntas
2. - [ ] Obtención de Datos
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
| 1 | ( ) | ( ) | ( ) | (X) |
| 2 | ( ) | ( ) | ( ) | ( ) |
| 3 | ( ) | ( ) | ( ) | ( ) |
| 4 | ( ) | ( ) | ( ) | ( ) |
| 5 | ( ) | ( ) | ( ) | ( ) |
| 6 | ( ) | ( ) | ( ) | ( ) |
| 7 | ( ) | ( ) | ( ) | ( ) |
| 8 | ( ) | ( ) | ( ) | ( ) |

## Estructura del Repositorio

- ./**data**: Datos obtenidos
    - /**pollution**: Datos de contaminación de sensores por CCAA
    - /*gini_ccaa.csv*: Índice de desigualdad GINI por CCAA
    - /*ipc_ccaa.csv*: Índice de Precios de Consumo por CCAA
    - /*pibc_ccaa.csv*: Producto Interior Bruto per capita por CCAA
    - /*pob_ccaa.csv*: Cantidad de población por CCAA
    - /*qol_ccaa.xslx*: Indice de calidad de vida por CCAA
    - /*qol_ccaa_ex.xslx*: Indice de calidad de vida por CCAA con muchos datos extra
- ./**design**: Diseños del almacen de datos
    - /*conceptual.md*: Diseño conceptual
    - /*logic.png*: Diesño lógico
    - /*physic.db*: Diseño físico
- ./**dist**: Agregados de datos final
- ./**docs**: Documentación del trabajo
    - /*Memoria.pdf*: Memoria final del trabajo
    - /*Memoria.odt*: Memoria del trabajo
- ./**kettle**: Trabajos y transformaciones de Pentaho
    - [NOTE] Idealmente las transformaciones compartiran nombre con los archivos sobre los que trabajan
    - /*.ktr*:
    - /*.kjb*:
- ./**visuals**: Visualizaciones de datos
    - /**gen**: Código para generar las visualizaciones
    - /*.png*

## Preguntas a Responder

- ¿Cómo influye la economia de una CCAA en la calidad de vida de sus habitantes?
- ¿Cómo influyen el turismo y la contaminación de una CCAA en la calidad de vida de sus habitantes?
- ¿Influye más la economia de la CCAA o su turismo y contaminación en la calidad de vida de sus habitantes?

## Datos Relevantes

Haremos uso de los siguientes datos para tratar de responder a estas preguntas.
Los datos agregaran la información por **Año**, fijandonos a poder ser en los más *recientes*,
por **CCAA** y sin tener en cuenta el **Sexo** de las personas.

- Contaminación del aire -> *pollution*
- Cantidad de población -> *pob_ccaa.csv*
- Indice de calidad de vida -> *qol_ccaa.xslx*
- Índice de precios de consumo -> *ipc_ccaa.csv*
- Producto interior bruto per capita -> *pibc_ccaa.csv*
- Índice de desigualdad económica GINI -> *gini_ccaa.csv*

## Agregación de Datos

La agregación de datos la realizaremos basandonos en las siguientes columnas.
Estas columnas deben tener **exactamente** el nombre indicado y sus valores tienen que estar **formateados** como se indica.

### CCAA

Contiene una de las siguientes Comunidades Autónomas como valor:

- andalucia 
- aragon
- asturias
- baleares
- canarias
- cantabria
- castilla_leon
- castilla_mancha
- catalunya
- ceuta_melilla
- comunidad_valenciana
- extremadura
- galicia
- madrid
- murcia
- navarra
- pais_vasco
- rioja

### Year

Contiene el año en formato YYYY como valor. Ej. 2025.

## Limpieza General de Datos

A la hora de procesar los datos, con las trasnformaciones de pentaho,
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
| ' ' | _ |

### Other

Todo lo demás que tengamos que hacer con los datos.

### Sort rows

Finalmente, ordenaremos los datos por las siguientes columnas:

1. [**Descendente**] Year
2. [**Ascendente**] CCAA

## Last Edited

21/11/25 - Stefano


