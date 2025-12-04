#!/bin/bash

scandir="../../data/pollution"

# PRIMER LOOP- FORMATEO y RATIOS
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

        echo "Procesando: $file"

        # Procesando con python:
        echo "CRIBADO INICIAL:"
        python3 cribadoInicial.py "$nom_region" "$(realpath "$file")"

        echo "FORMATEO: COLUMNAS"
        if [ "$nom_region" == "castilla_mancha" ]; then
            python3 formateadorLaMancha.py "$(realpath "$file")"
        else
            echo "NO PASA NADA"
            python3 formateador.py "$nom_region" "$(realpath "$file")"
        fi

        echo "POST_CAMBIOS"
        python3 cribadoFormateado.py "$nom_region" "$(realpath "$file")"

        echo "CALCULANDO RATIOS:"
        python3 ratioMaker.py "$nom_region" "$(realpath "$file")"
    done
done

# SEGUNDO LOOP - ARREGLO RATOS
for region in "$scandir"/*/; do 
    python3 inferenciaVecinos.py "$region"
done 

# TERCER LOOP - INFERENCIA DE DATOS
for region in "$scandir"/*/; do 
    nom_region="$(basename "$region")"
    for file in "$region"/*.csv; do 

        [ -e "$file" ] || continue 

        echo "INFERENCIA PM25 en \n$file"
        python3 inferencia25.py "$nom_region" "$(realpath "$file")"
        echo "INFERENCIA CONTAMINANTES en \n$file"
        python3 inferenciaContaminantes.py "$nom_region" "$(realpath "$file")"
    done 
done 

# CUARTO LOOP - AGREGACIÓN

super_csv="../../data/pollution/super.csv"

# Crear super.csv si no existe
echo "date;region;pm25;pm10;o3;no2;so2;co" > "$super_csv"

for region in "$scandir"/*/; do
    nom_region="$(basename "$region")"
    for file in "$region"/*.csv; do

        [ -e "$file" ] || continue

        # Añadir filas a super.csv
        # añadiendo columna region, simplificando fecha.
        # Nos Saltamos el cabezal.
        awk -F';' -v OFS=';' -v region="$nom_region" 'NR>1 {
            split($1,d,"-");   # assuming $1 is date
            year=d[1];
            print year, region, $2, $3, $4, $5, $6, $7
        }' "$file" >> "$super_csv"

    done
done

echo "Super CSV created at $super_csv"

# QUINTO PASO - FACTORIZACIÓN
echo "Generando total_polution.csv agregando por año y región..."
python3 total_polution.py