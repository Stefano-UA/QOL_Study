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

scandir="../../temp/pollution"
SUPER_CSV="../../temp/pollution/super.csv"

echo "################################################"
echo "#  2a Etapa - AGREGACIÓN CENTRAL (SUPER_CSV)   #"
echo "################################################"

# Inicializamos SUPER_CSV 
echo "year;region;sensor;pm25;pm10;o3;no2;so2;co" > "$SUPER_CSV"

for region in "$scandir"/*/; do
    nom_region="$(basename "$region")"
    echo "Trabajando en la Región: $nom_region"
    for file in "$region"/*.csv; do
        [ -e "$file" ] || continue

        # 1. Extracción del sensor
        base_name="$(basename "$file")"
        sensor_id="${base_name:0:10}"
        
        echo "Añadiendo: \n $file (ID: $sensor_id)"
        
        # 2. AWK para añadir year, region, id, y anexar
        awk -F';' -v OFS=';' -v region="$nom_region" -v file_id="$sensor_id" 'NR>1 {
            split($1,d,"[/]");
            year=d[1];
            if (region=="castilla_mancha") region="castilla_la_mancha"
            if (region=="la_rioja") region="rioja"
            
            # Orden: year, region, sensor_id, contaminantes
            print year, region, sensor_id, $2, $3, $4, $5, $6, $7
        }' "$file" >> "$SUPER_CSV"
    done
done

echo "########################"
echo "# 3a Etapa - PATRONES  #"
echo "########################" 
echo "----Calculando Ratios por (YEAR, REGION, SENSOR) y Nacional..."
python3 ratios.py 

echo "###################################"
echo "# 4a Etapa - INFERENCIA DE DATOS (Centralizada) #"
echo "###################################"
echo "----Aplicando Inferencia sobre SUPER_CSV..."
python3 inferencia.py 

echo "#############################"
echo "# 5a Etapa - FACTORIZACIÓN  #"
echo "#############################"
echo "Generando pollution.csv agregando por año, región y tipo:"
python3 agregador.py

# LIMPIEZA
deactivate
rm -rf .venv