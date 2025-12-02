#!/bin/bash
echo "funciona"

scandir="../../data/pollution"

for region in "$scandir"/*/; do
    for file in "$region"/*.csv; do
        
        # Skip if file doesn't exist
        [ -e "$file" ] || continue

        # Remove spaces in filename
        cleaned="${file// /}"
        if [ "$file" != "$cleaned" ]; then
            mv "$file" "$cleaned"
            file="$cleaned"
        fi 

        echo "Processing: $file"

        # Run python script for the file
        python3 experimento.py "$(basename "$region")" "$(realpath "$file")"

    done
done
