#!/bin/bash

scandir="../../data/pollution"

for region in "$scandir"/*/; do
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
        echo "CRIBADO:"
        python3 cribado.py "$(basename "$region")" "$(realpath "$file")"
        #echo "FORMATEO: COLUMNAS"
        #python3 formateador.py "$(basename "$region")" "$(realpath "$file")"

    done
done
