#!/bin/bash

# bash options
set -o errexit
set -o nounset
set -o pipefail

# for debugging
set -o xtrace

# Activate python environment
. "/home/jvhaarst/miniconda3/etc/profile.d/conda.sh"
conda activate scrape

# Change to data folder
cd /home/jvhaarst/public_html/

# Get data
python scrape_zonnepanelen.py

# Create graphs of all data
python analyse.py

# Create graphs of panels with glas keyword
python analyse.py glas


# create new index.html from last result for local view 
ln -f $(ls -trh *xz.html | tail -1) index.html

# Push new result to github
git checkout results

# create new index.html from last result for github.io
ln -f $(ls -trh *xz.html | tail -1) index.html

git add index.html
git commit -m "New result" index.html
git checkout main
git push origin results
