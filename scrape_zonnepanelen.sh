#!/bin/bash

# Activate python environment
. "${HOME}/miniconda3/etc/profile.d/conda.sh"
conda activate scrape

# bash options
set -o errexit
set -o nounset
set -o pipefail

# for debugging
#set -o xtrace


# Change to data folder
cd ~/public_html/

# Get data
python scrape_zonnepanelen.py

# Create graphs of all data
python analyse.py

# Create graphs of panels with glas keyword
python analyse.py glas

# create new index.html from last result for local view 
#ln -f $(ls -trh *xz.html | tail -1) index.html
