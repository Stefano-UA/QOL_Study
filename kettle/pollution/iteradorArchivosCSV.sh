#!/bin/bash

scandir="../../data/pollution"

for region in "$scandir"/*/; do
    #echo same_format.py "$(basename "$region")" "$(realpath "$region"/*.csv)"
    for file in "$region"/*.csv; do
        if [ "$file" != "${file// /}" ]; then
            mv "$file" "${file// /}"
        fi
        
    done
done