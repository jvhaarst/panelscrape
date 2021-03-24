#!/bin/bash
. "/home/jvhaarst/miniconda3/etc/profile.d/conda.sh"
conda activate scrape
cd /home/jvhaarst/public_html/
python scrape_zonnepanelen.py
python analyse.py

#FILE=$(ls -tr zonnepanelen.*.csv.xz | grep -v glas | tail -1)
#NEW_FILE=${FILE%.csv.xz}.glas.csv
#xzcat $FILE | head -1 > $NEW_FILE
#xzgrep -i glas $FILE >> $NEW_FILE
#xz -f $NEW_FILE

python analyse.py glas
