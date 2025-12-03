#!/bin/bash

scandir="../../data/pollution"

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

        echo "Processing: $file"

        # Procesando con python:
#        echo "CRIBADO INICIAL:"
#        python3 cribadoInicial.py "$(basename "$region")" "$(realpath "$file")"
#        echo "FORMATEO: COLUMNAS"
#        if [ "$nom_region" == "castilla_mancha" ]; then
#            echo "JALIBU"
#            python3 formateadorLaMancha.py "$(realpath "$file")"
#        else
#            echo "NO PASA NADA"
#            python3 formateador.py "$(basename "$region")" "$(realpath "$file")"
#        fi
#        echo "POST_CAMBIOS"
#        python3 cribadoFormateado.py "$(basename "$region")" "$(realpath "$file")"
#        echo "CALCULANDO RATIOS:"
        python3 ratioMaker.py "$nom_region" "$(realpath "$file")"
    done
done
