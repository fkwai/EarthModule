import tensorflow as tf
import ee
import folium
import webbrowser

EE_TILES = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}'
ee.Initialize()

l7sr = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')
image = l7sr.filterDate('2018-01-01', '2018-12-31').select('B[1-7]')

# Use folium to visualize the imagery.
mapid = image.getMapId({'bands': ['B4', 'B3', 'B2']})
map = folium.Map(location=[38., -122.5])
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='median composite',
).add_to(map)
map.add_child(folium.LayerControl())
map.save('map.html')
webbrowser.open('map.html')

# Change the following two lines to use your own training data.
labels = ee.FeatureCollection('projects/google/demo_landcover_labels')
label = 'landcover'

# Sample the image at the points and add a random column.
sample = image.sampleRegions(
  collection=labels, properties=[label], scale=30).randomColumn()

# Partition the sample approximately 70-30.
training = sample.filter(ee.Filter.lt('random', 0.7))
testing = sample.filter(ee.Filter.gte('random', 0.7))

from pprint import pprint

# Print the first couple points to verify.
pprint({'training': training.first().getInfo()})
pprint({'testing': testing.first().getInfo()})
