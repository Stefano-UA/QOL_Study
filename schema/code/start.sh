#!/bin/bash
# <============================================>

#   ███████╗████████╗ █████╗ ██████╗ ████████╗
#   ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝
#   ███████╗   ██║   ███████║██████╔╝   ██║
#   ╚════██║   ██║   ██╔══██║██╔══██╗   ██║
#   ███████║   ██║   ██║  ██║██║  ██║   ██║
#   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝

# <============================================>
#   Sets up the environment and makes the RDF
# <============================================>
#  Configuration:
# <============================================>
WKDIR="$(dirname "${BASH_SOURCE[0]}")"
VENVDIR="${WKDIR}/../../.venv"
# <============================================>
#  Create the python venv:
# <============================================>
echo "Creating Python virtual environment..."
python3 -m venv "$VENVDIR"
# <============================================>
#  Install the required dependencies:
# <============================================>
echo "Installing required Python packages in virtual environment..."
"${VENVDIR}/bin/pip" install --quiet --upgrade pip
"${VENVDIR}/bin/pip" install --quiet rdflib pandas
# <============================================>
#  Execute the python script to make the plots:
# <============================================>
echo "Executing Python script..."
"${VENVDIR}/bin/python" "${WKDIR}/transform_rdf.py"
echo "Finished executing script!"
# <============================================>
