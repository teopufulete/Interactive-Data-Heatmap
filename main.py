import geopandas as gpd
import pandas as pd
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, HoverTool
from bokeh.layouts import widgetbox, row, column


shapefile = 'data/countries/ne_110m_admin_0_countries.shp'
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]        # read country data
gdf.columns = ['country', 'country_code', 'geometry']       # rename columns.
gdf.head()
print(gdf[gdf['country'] == 'Antarctica'])
gdf = gdf.drop(gdf.index[159])      #drop Antarctica row as no humans live there

datafile = 'data/obesity.csv'
df = pd.read_csv(datafile, names = ['entity', 'code', 'year', 'per_cent_obesity'], skiprows = 1)        # read csv file using
df.head()

df_2016 = df[df['year'] == 2016]  # filter 2016 data .
merged = gdf.merge(df_2016, left_on = 'country_code', right_on = 'code', how = 'left')      # merge gdf and df_2016.


merged_json = json.loads(merged.to_json())     # data to json
json_data = json.dumps(merged_json)      # convert to String like object.


# geosource = GeoJSONDataSource(geojson = json_data)
# palette = brewer['YlGnBu'][8]
# palette = palette[::-1]     # reverse color order of palette
# color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40)     # map numbers in a range to a sequence of colors
#
# tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}
#
# color_bar = ColorBar(color_mapper=color_mapper,
#                      label_standoff=8,
#                      width = 500, height = 20,
#                      border_line_color=None,
#                      location = (0,0), orientation = 'horizontal',
#                      major_label_overrides = tick_labels)
#
# p = figure(title = 'Share of adults who are obese, 2016',
#            plot_height = 600 , plot_width = 950,
#            toolbar_location = None)
# p.xgrid.grid_line_color = None
# p.ygrid.grid_line_color = None
# p.patches('xs','ys', source = geosource,
#           fill_color = {'field' :'per_cent_obesity', 'transform' : color_mapper},
#           line_color = 'black', line_width = 0.25, fill_alpha = 1)
# p.add_layout(color_bar, 'below')
# show(p)


def json_data(selectedYear):        # function returns json_data for year selected by user.
    yr = selectedYear
    df_yr = df[df['year'] == yr]
    merged = gdf.merge(df_yr, left_on='country_code', right_on='code', how='left')
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data

geosource = GeoJSONDataSource(geojson=json_data(2016))
palette = brewer['RdPu'][8]
palette = palette[::-1]
color_mapper = LinearColorMapper(palette=palette, low=0, high=40, nan_color='#d9d9d9')
tick_labels = {'0': '0%', '5': '5%', '10': '10%', '15': '15%', '20': '20%', '25': '25%', '30': '30%', '35': '35%',
               '40': '>40%'}
hover = HoverTool(tooltips=[('Country/region', '@country'), ('% obesity', '@per_cent_obesity')])

color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                     border_line_color=None, location=(0, 0), orientation='horizontal',
                     major_label_overrides=tick_labels)

p = figure(title='Share of adults who are obese, 2016', plot_height=600, plot_width=950, toolbar_location=None,
           tools=[hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.patches('xs', 'ys', source=geosource,
          fill_color={'field': 'per_cent_obesity', 'transform': color_mapper},
          line_color='black', line_width=0.25, fill_alpha=1)
p.add_layout(color_bar, 'below')

def update_plot(attr, old, new):
    yr = slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    p.title.text = 'Share of adults who are obese, %d' % yr

slider = Slider(title='Year', start=1975, end=2016, step=1, value=2016)
slider.on_change('value', update_plot)

layout = column(p, widgetbox(slider))
curdoc().add_root(layout)
show(layout)