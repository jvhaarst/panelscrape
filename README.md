#PanelScrape

This project uses Python to grab, parse and analyse data from solar panel vendors in the Netherlands

One shop needs manual filling in `````solarwindbioshop.xlsx`````, as that site can't be scraped.

## Results
The see the last result, go here : https://jvhaarst.github.io/panelscrape/

## Installation
To get this running in your own environment, you will need to install Conda : https://conda.io

After that, create the necessary environment:
```bash
conda create -n scrape python=3 pandas seaborn bokeh bs4 lxml requests xlrd openpyxl
```

## Usage

To grab, parse and analyse the data, run `````scrape_zonnepanelen.sh`````

## Extras

`````get_nember_of_sites.py````` can be used to check whether all sites are returning results

`````get_nember_of_priceless_entries.py````` can be used to check whether all prices are present for all panels

`````push_results.sh````` is a small script to upload the latest result to github in a separate branch.