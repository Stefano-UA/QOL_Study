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