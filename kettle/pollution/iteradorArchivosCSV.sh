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
        echo "----Cribado Inicial:"
        python3 cribadoInicial.py "$nom_region" "$(realpath "$file")"

        echo "----Formateo:"
        if [ "$(basename "$file")" == "2025-11-06_sds011_sensor_83475.csv" ]; then
            python3 formateadorLaMancha.py "$(realpath "$file")"
        else
            python3 formateador.py "$nom_region" "$(realpath "$file")"
        fi

        echo "----Cribado Final:"
        python3 cribadoFormateado.py "$nom_region" "$(realpath "$file")"
    done
done

# SEGUNDO LOOP- RATIOS
echo "###################################"
echo "#  2a Etapa - PATRONES INICIALES  #"
echo "###################################"

for region in "$scandir"/*/; do
    nom_region="$(basename "$region")"
    echo "Trabajando en la Región: $nom_region"
    for file in "$region"/*.csv; do

    echo "Procesando: \n$file"
    echo "----Analizando Patrones:"
    python3 ratios.py "$nom_region" "$(realpath "$file")"
    done
done

# TERCER LOOP- RATIO NACIONAL
echo "###################################"
echo "# 3a Etapa - PATRONES NACIONALES  #"
echo "###################################"

echo "----Consiguiendo Patrones Nacionales"
python3 ratiosNacional.py

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
        inferred_file="${file%.csv}_inferred.csv"
        [ -e "$inferred_file" ] || continue

        echo "Añadiendo $inferred_file"
        # Añadir filas a super.csv
        # añadiendo columna region, simplificando fecha.
        # Nos Saltamos el cabezal.
        awk -F';' -v OFS=';' -v region="$nom_region" 'NR>1 {
            split($1,d,"[-/]");   # assuming $1 is date
            year=d[1];
            if (region=="castilla_mancha") region="castilla_la_mancha"
            if (region=="la_rioja") region="rioja"
            print year, region, $2, $3, $4, $5, $6, $7
        }' "$inferred_file" >> "$SUPER_CSV"
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