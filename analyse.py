#!/usr/bin/env python
# coding: utf-8

# Analysis imports
import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
import datetime

import os
import sys
from glob import iglob

from bokeh.io import output_notebook, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool, OpenURL, TapTool
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.transform import jitter
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

# Get newest csv file
filename = max(iglob('*.csv.xz'), key=os.path.getmtime)
graphfile = filename+'.html'

df1 = pd.read_csv(filename,index_col=0)
df2 = pd.read_excel('solarwindbioshop.xlsx')

df = pd.concat([df1,df2],sort=False)

# Fix some of the panels with 0 power value.
# TODO : Make this nicer, so we do not do it in 4 steps
more_power = df[df.power.eq(0)]['Naam'].str.extract('([1234]\d{2})')
more_power.columns = ['power']
more_power['power'] = more_power['power'].astype(float)
df.update(more_power)

df = df[df['power'].gt(200)]
df = df[df['Prijs'].gt(0)]
df = df[df['Prijs'].lt(1000)]

df['€/Wp']=df['Prijs']/df['power']
cheapest = df['€/Wp'].min()
df['% tov min €/Wp']=(df['€/Wp']/cheapest * 100) - 100

# Filter on keyword if present
if len (sys.argv) >1 :
    keyword = sys.argv[1]
    df = df[df['Naam'].str.contains(keyword,case=False)]
    graphfile = filename+'.'+keyword+'.html'


source = ColumnDataSource(df)
tools = "box_zoom, undo,tap"
shops=df['Shop'].unique()

# First plot, price
s1 = figure(width=1600, height=800,tools=tools,title="PV panelen prijzen - "+datetime.date.today().isoformat())
s1.xaxis.axis_label = 'Wp'
s1.yaxis.axis_label = '€'
s1.scatter('power','Prijs', source=source, legend_field="Shop", fill_alpha=0.5, size=7,
         color=factor_cmap('Shop','Category20_13', shops))
s1.add_tools(
    HoverTool(
        tooltips=[('Prijs','€@Prijs{2.2f}'),
                  ('Wp'   ,'@power{0}'),
                  ('Shop' ,'@Shop'),
                  ('Naam' ,'@Naam'),
                  ('€/Wp' ,'@{€/Wp}'),
                  ('% tov min €/Wp' ,'+@{% tov min €/Wp}{2.1f}%')
                 ]
    )
)
s1.legend.location = "top_left"
taptool_1 = s1.select(type=TapTool)
taptool_1.callback = OpenURL(url="@URL")

# Second plot, percentage difference wrt minimal price/Wp
s2 = figure(width=1600, height=800,tools=tools,title="PV panelen prijzen - "+datetime.date.today().isoformat())
s2.xaxis.axis_label = 'Wp'
s2.yaxis.axis_label = '% tov min €/Wp'
s2.scatter('power','% tov min €/Wp', source=source, legend_field="Shop", fill_alpha=0.5, size=7,
         color=factor_cmap('Shop','Category20_13', shops))
s2.add_tools(
    HoverTool(
        tooltips=[('Prijs','€@Prijs{2.2f}'),
                  ('Wp'   ,'@power{0}'),
                  ('Shop' ,'@Shop'),
                  ('Naam' ,'@Naam'),
                  ('€/Wp' ,'@{€/Wp}'),
                  ('% tov min €/Wp' ,'+@{% tov min €/Wp}{2.1f}%')
                 ]
    )
)
s2.legend.location = "top_left"
taptool_2 = s2.select(type=TapTool)
taptool_2.callback = OpenURL(url="@URL")
# Add more values to x axis labels
# round to 10
start_ticker = round(int(df.power.values.min())/10)*10
end_ticker = round(int(df.power.values.max())/10)*10
s1.xaxis.ticker = list(range(start_ticker,end_ticker,10))
s2.xaxis.ticker = list(range(start_ticker,end_ticker,10))
# put all the plots in a VBox
p = column(s1, s2)

# create a complete HTML file
html = file_html(p, CDN, "p")

# write the file
newfile = open(graphfile, 'w')
newfile.write(html)
newfile.close()
