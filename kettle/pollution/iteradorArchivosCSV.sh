#!/bin/bash

# PRELIMINAR - COPIAMOS LA INFORMACIÓN
rm -rf ../../temp/pollution
mkdir -p ../../temp/pollution
cp -r ../../data/pollution/* ../../temp/pollution/

# PRELIMINAR - ENTORNO PYTHON
python3 -m venv .venv
source .venv/bin/activate
pip install --quiet -r requirements.txt

scandir="../../temp/pollution"

# PRIMER LOOP- FORMATEO
echo "###########################"
echo "#  1a Etapa - FORMATEO    #"
echo "###########################"

for region in "$scandir"/*/; do
    nom_region="$(basename "$region")"
    for file in "$region"/*.csv; do

        # Nos lo saltamos sino existe
        [ -e "$file" ] || continue
        # Quitamos Espacios en los nombres.
        cleaned="${file// /}"
        if [ "$file" != "$cleaned" ]; then
            mv "$file" "$cleaned"
            file="$cleaned"
        fi 

        echo "Procesando: \n$file"
        echo "----Formateo:"
        if [ "$(basename "$file")" == "2025-11-06_sds011_sensor_83475.csv" ]; then
            python3 formateadorLaMancha.py "$(realpath "$file")"
        else
            python3 formateador.py "$nom_region" "$(realpath "$file")"
        fi
    done
done

# SEXTO LOOP- AGREGACIÓN
echo "##########################"
echo "# 6a Etapa - AGREGACIÓN  #"
echo "##########################"

SUPER_CSV="../../temp/pollution/super.csv"
rm -f "$SUPER_CSV"

# Nuevo Encabezado: Incluye 'id' en la tercera posición
echo "year;region;sensor;pm25;pm10;o3;no2;so2;co" > "$SUPER_CSV"

for region in "$scandir"/*/; do
    nom_region="$(basename "$region")"
    echo "Trabajando en la Región: $nom_region"
    for file in "$region"/*.csv; do
        [ -e "$file" ] || continue

        # 1. EXTRACCIÓN DEL ID (Primeros 10 caracteres del nombre del archivo)
        # Obtenemos solo el nombre base (ej: 2025-11-06_sds011_sensor_83475.csv)
        base_name="$(basename "$file")"
        # Obtenemos los primeros 10 caracteres (ej: 2025-11-06)
        file_id="${base_name:0:10}"
        
        echo "Añadiendo: \n $file (ID: $file_id)"
        
        # AWK MODIFICADO: Ahora recibe 'file_id' y lo imprime en tercer lugar
        awk -F';' -v OFS=';' -v region="$nom_region" -v file_id="$file_id" 'NR>1 {
            # 1. Simplificar fecha a solo el año (year)
            split($1,d,"[/]");
            year=d[1];
            
            # 2. Estandarizar el nombre de la región
            if (region=="castilla_mancha") region="castilla_la_mancha"
            if (region=="la_rioja") region="rioja"
            
            # 3. Imprimir en el orden requerido: year, region, id, contaminantes
            print year, region, file_id, $2, $3, $4, $5, $6, $7
        }' "$file" >> "$SUPER_CSV"
    done
done




# SEGUNDO LOOP- RATIOS
echo "###################################"
echo "#  2a Etapa - PATRONES INICIALES  #"
echo "###################################"

echo "----Analizando Patrones:"
python3 ratios.py "$nom_region" "$(realpath "$file")"


# TERCER LOOP- RATIO NACIONAL
echo "###################################"
echo "# 3a Etapa - PATRONES NACIONALES  #"
echo "###################################" # IDENTIFICADOR?

echo "----Consiguiendo Patrones Nacionales"
python3 ratiosNacional.py

NACIONAL_RATIOS="../../temp/pollution/nacional_ratios.csv"
for region in "$scandir"/*/; do
    nom_region="$(basename "$region")"
    tail -n +2 "$NACIONAL_RATIOS" >> "$region/${nom_region}_ratios.csv"
done 


# CUARTO LOOP- INFERENCIA RATIOS
echo "###################################"
echo "# 4a Etapa - INFERENCIA PATRONES  #"
echo "###################################"

for region in "$scandir"/*/; do 
    echo "Trabjando con $(basename "$region")"
    echo "----Inferencia de Patrones de la Región"
    python3 ratiosInferencia.py "$region"
done 

# QUINTO LOOP- INFERENCIA DE DATOS
echo "###################################"
echo "# 5a Etapa - INFERENCIA DE DATOS  #"
echo "###################################"
for region in "$scandir"/*/; do 
    nom_region="$(basename "$region")"
    echo "Trabajando en la Región: $nom_region"
    for file in "$region"/*.csv; do 
        [ -e "$file" ] || continue 

        echo "Procesando \n$file"
        echo "----Inferencia de PM25 y otros Comntaminantes: "
        python3 inferencia.py "$nom_region" "$(realpath "$file")"
    done 
done 

# SEXTO LOOP- AGREGACIÓN
echo "##########################"
echo "# 6a Etapa - AGREGACIÓN  #"
echo "##########################"

SUPER_CSV="../../temp/pollution/super.csv"
rm -f "$SUPER_CSV"
echo "date;region;pm25;pm10;o3;no2;so2;co" > "$SUPER_CSV"

for region in "$scandir"/*/; do
    nom_region="$(basename "$region")"
    echo "Trabajando en la Región: $nom_region"
    for file in "$region"/*.csv; do
        [ -e "$file" ] || continue

        echo "Añadiendo: \n $file"
        # Añadir filas a super.csv
        # añadiendo columna region, simplificando fecha.
        # Nos Saltamos el cabezal.
        awk -F';' -v OFS=';' -v region="$nom_region" 'NR>1 {
            split($1,d,"[-/]");   # assuming $1 is date
            year=d[1];
            if (region=="castilla_mancha") region="castilla_la_mancha"
            if (region=="la_rioja") region="rioja"
            print year, region, $2, $3, $4, $5, $6, $7
        }' "$file" >> "$SUPER_CSV"
    done
done


# ÚLTIMO PASO - FACTORIZACIÓN
echo "#############################"
echo "# 7a Etapa - FACTORIZACIÓN  #"
echo "#############################"
echo "Generando pollution.csv agregando por año, región y tipo:"
python3 agregador.py

# LIMPIEZA
deactivate
rm -rf .venv