import tensorflow as tf
import ee
import folium
import webbrowser

EE_TILES = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}'
ee.Initialize()

# 33
BUCKET = 'deepldb'
# Specify names locations for outputs in Cloud Storage.
FOLDER = 'fcnn-demo'
TRAINING_BASE = 'training_patches'
EVAL_BASE = 'eval_patches'

# Specify inputs (Landsat bands) to the model and the response variable.
opticalBands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']
thermalBands = ['B10', 'B11']
BANDS = opticalBands + thermalBands
RESPONSE = 'impervious'
FEATURES = BANDS + [RESPONSE]

# Specify the size and shape of patches expected by the model.
KERNEL_SIZE = 256
KERNEL_SHAPE = [KERNEL_SIZE, KERNEL_SIZE]
COLUMNS = [
    tf.io.FixedLenFeature(shape=KERNEL_SHAPE, dtype=tf.float32) for k in FEATURES
]
FEATURES_DICT = dict(zip(FEATURES, COLUMNS))

# Sizes of the training and evaluation datasets.
TRAIN_SIZE = 16000
EVAL_SIZE = 8000

# Specify model training parameters.
BATCH_SIZE = 16
EPOCHS = 10
BUFFER_SIZE = 2000
OPTIMIZER = 'SGD'
LOSS = 'MeanSquaredError'
METRICS = ['RootMeanSquaredError']


#################################################################################

# Use Landsat 8 surface reflectance data.
l8sr = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')

# Cloud masking function.


def maskL8sr(image):
    cloudShadowBitMask = ee.Number(2).pow(3).int()
    cloudsBitMask = ee.Number(2).pow(5).int()
    qa = image.select('pixel_qa')
    mask1 = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
        qa.bitwiseAnd(cloudsBitMask).eq(0))
    mask2 = image.mask().reduce('min')
    mask3 = image.select(opticalBands).gt(0).And(
        image.select(opticalBands).lt(10000)).reduce('min')
    mask = mask1.And(mask2).And(mask3)
    return image.select(opticalBands).divide(10000).addBands(
        image.select(thermalBands).divide(10).clamp(273.15, 373.15)
        .subtract(273.15).divide(100)).updateMask(mask)


# The image input data is a cloud-masked median composite.
image = l8sr.filterDate('2015-01-01', '2017-12-31').map(maskL8sr).median()

# Use folium to visualize the imagery.
mapid = image.getMapId({'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3})
map = folium.Map(location=[38., -122.5])
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='median composite',
).add_to(map)
mapid = image.getMapId({'bands': ['B10'], 'min': 0, 'max': 0.5})
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='thermal',
).add_to(map)
nlcd = ee.Image('USGS/NLCD/NLCD2016').select('impervious')
nlcd = nlcd.divide(100).float()
mapid = nlcd.getMapId({'min': 0, 'max': 1})
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='nlcd impervious',
).add_to(map)
map.add_child(folium.LayerControl())
map.save('map.html')
webbrowser.open('map.html')

#################################################################################
featureStack = ee.Image.cat([
    image.select(BANDS),
    nlcd.select(RESPONSE)
]).float()

lst = ee.List.repeat(1, KERNEL_SIZE)
lists = ee.List.repeat(lst, KERNEL_SIZE)
kernel = ee.Kernel.fixed(KERNEL_SIZE, KERNEL_SIZE, lists)
arrays = featureStack.neighborhoodToArray(kernel)

map = folium.Map(location=[38., -122.5])
mapid = arrays.getMapId({'bands': ['B4', 'B3', 'B2']})
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='test',
).add_to(map)
map.add_child(folium.LayerControl())
map.save('map.html')
webbrowser.open('map.html')

dimensions = ee.Dictionary(ee.List(ee.Dictionary(
    ee.Algorithms.Describe(arrays)).get('bands')).get(0)).get('dimensions')


###################
trainingPolys = ee.FeatureCollection('projects/google/DemoTrainingGeometries')
evalPolys = ee.FeatureCollection('projects/google/DemoEvalGeometries')

polyImage = ee.Image(0).byte().paint(trainingPolys, 1).paint(evalPolys, 2)
polyImage = polyImage.updateMask(polyImage)

mapid = polyImage.getMapId({'min': 1, 'max': 2, 'palette': ['red', 'blue']})
map = folium.Map(location=[38., -100.], zoom_start=5)
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='training polygons',
).add_to(map)
map.add_child(folium.LayerControl())
map.add_child(folium.LayerControl())
map.save('map.html')
webbrowser.open('map.html')

#################################
# Convert the feature collections to lists for iteration.
trainingPolysList = trainingPolys.toList(trainingPolys.size())
evalPolysList = trainingPolys.toList(trainingPolys.size())

# These numbers determined experimentally.
n = 100  # Number of shards in each polygon.
N = 2000  # Total sample size in each polygon.

geomSample = ee.FeatureCollection([])
sample = arrays.sample(
    region=ee.Feature(trainingPolysList.get(0)).geometry(),
    scale=30,
    numPixels=N / n,  # Size of the shard.
    seed=1,
    tileScale=8
)

# Export all the training data (in many pieces), with one task
# per geometry.
# for g in range(trainingPolys.size().getInfo()):
#   geomSample = ee.FeatureCollection([])
#   for i in range(n):
#     sample = arrays.sample(
#         region=ee.Feature(trainingPolysList.get(g)).geometry(),
#         scale=30,
#         numPixels=N / n,  # Size of the shard.
#         seed=i,
#         tileScale=8
#     )
#     geomSample = geomSample.merge(sample)

#   desc = TRAINING_BASE + '_g' + str(g)
#   task = ee.batch.Export.table.toCloudStorage(
#       collection=geomSample,
#       description=desc,
#       bucket=BUCKET,
#       fileNamePrefix=FOLDER + '/' + desc,
#       fileFormat='TFRecord',
#       selectors=BANDS + [RESPONSE]
#   )
#   task.start()

# # Export all the evaluation data.
# for g in range(evalPolys.size().getInfo()):
#   geomSample = ee.FeatureCollection([])
#   for i in range(n):
#     sample = arrays.sample(
#         region=ee.Feature(evalPolysList.get(g)).geometry(),
#         scale=30,
#         numPixels=N / n,
#         seed=i,
#         tileScale=8
#     )
#     geomSample = geomSample.merge(sample)

#   desc = EVAL_BASE + '_g' + str(g)
#   task = ee.batch.Export.table.toCloudStorage(
#       collection=geomSample,
#       description=desc,
#       bucket=BUCKET,
#       fileNamePrefix=FOLDER + '/' + desc,
#       fileFormat='TFRecord',
#       selectors=BANDS + [RESPONSE]
#   )
#   task.start()
