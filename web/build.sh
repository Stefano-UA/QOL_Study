#!/bin/bash
# <=======================================================>

#   ██╗    ██╗███████╗██████╗  ██████╗ ███████╗███╗   ██╗
#   ██║    ██║██╔════╝██╔══██╗██╔════╝ ██╔════╝████╗  ██║
#   ██║ █╗ ██║█████╗  ██████╔╝██║  ███╗█████╗  ██╔██╗ ██║
#   ██║███╗██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██║╚██╗██║
#   ╚███╔███╔╝███████╗██████╔╝╚██████╔╝███████╗██║ ╚████║
#    ╚══╝╚══╝ ╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═══╝

# <=======================================================>
#      Generates static web page using HTML snippets
# <=======================================================>
#  Stop on error
# <=======================================================>
set -e
# <=======================================================>
#  Configuration & Constants:
# <=======================================================>
#  Script directory
# <=======================================================>
WKDIR="$(dirname "${BASH_SOURCE[0]}")"
# <=======================================================>
#  HTML Snippets
# <=======================================================>
HEADER_SNP="${WKDIR}/header.html"
FOOTER_SNP="${WKDIR}/footer.html"
CARD_SNP="${WKDIR}/card.html"
# <=======================================================>
#  Input directory
# <=======================================================>
MAPS_DIR="${WKDIR}/../visuals/extended"
# <=======================================================>
#  Output directory
# <=======================================================>
DIST_DIR="${WKDIR}/../dist/web"
# <=======================================================>
#  Maps subdirectory
# <=======================================================>
DIST_MAPS="${DIST_DIR}/maps"
# <=======================================================>
#  Code:
# <=======================================================>
#  Clean and create directories
# <=======================================================>
echo " -> Cleaning output directory: ${DIST_DIR}"
# <=======================================================>
rm -rf "$DIST_DIR"; mkdir -p "$DIST_MAPS";
# <=======================================================>
#  Check if maps exist
# <=======================================================>
if ! ls "$MAPS_DIR"/map_*.html 1> /dev/null 2>&1; then
    echo " [ERROR] No maps found in ${MAPS_DIR}. Please run extended.py first."
    exit 1
fi
# <=======================================================>
#  Copy map files to distribution folder
# <=======================================================>
echo " -> Copying maps from ${MAPS_DIR}..."
cp "${MAPS_DIR}"/map_*.html "${DIST_MAPS}/"
# <=======================================================>
#  Generate index.html
# <=======================================================>
INDEX_FILE="${DIST_DIR}/index.html"
# <=======================================================>
echo " -> Building ${INDEX_FILE} from snippets..."
# <=======================================================>
#  1. Inject Header
# <=======================================================>
if [ -f "$HEADER_SNP" ]; then
    cat "$HEADER_SNP" > "$HEADER_SNP"
else
    echo " [ERROR] Header template not found at ${HEADER_TPL}"
    exit 1
fi
# <=======================================================>
#  2. Inject Cards (Loop & Replace)
# <=======================================================>
if [ -f "$CARD_SNP" ]; then
    # Loop trough maps
    for map in "${DIST_MAPS}"/*.html; do
        filename=$(basename "$map")
        # Format title: (remove prefix, extension, underscores; spaces, capitalize)
        title=$(echo "$filename" | sed -e 's/mapa_//' -e 's/.html//' -e 's/_/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
        # URL relative to index.html
        url="maps/${filename}"
        # Read card snippet, replace placeholders using sed, and append to index
        sed -e "s|{{URL}}|${url}|g" -e "s|{{TITLE}}|${title}|g" "$CARD_SNP" >> "$INDEX_FILE"
    done
else
    echo " [ERROR] Card template not found at ${CARD_SNP}"
    exit 1
fi
# <=======================================================>
#  3. Inject Footer
# <=======================================================>
if [ -f "$FOOTER_SNP" ]; then
    cat "$FOOTER_SNP" >> "$FOOTER_SNP"
else
    echo " [ERROR] Footer template not found at ${FOOTER_SNP}"
    exit 1
fi
# <=======================================================>
#  End of Script
# <=======================================================>
echo " -> Success! Website generated at: ${DIST_DIR}/index.html"
# <=======================================================>