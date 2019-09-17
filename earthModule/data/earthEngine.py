import tensorflow as tf
import ee
import folium
import webbrowser
import earthModule
from earthModule.data import landSlide
# import .landSlide
ee.Initialize()

fileNamePre = 'GE_39.667262_-105.280804_39.667973_-105.279188_20121007_PRE'
fileNamePost = 'GE_39.667262_-105.280804_39.667973_-105.279188_20131006_POST'
folder=r'C:\Users\geofk\work\earthModule\earthModule\data\landSlide'

bb, t1 = landSlide.readFileInfo(fileNamePre)
bb, t2 = landSlide.readFileInfo(fileNamePost)

imageCol = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(
    t1, t2).filterBounds(bb).select('B[1-7]')

image = ee.Image(imageCol.toList(imageCol.size()).get(0))
task = ee.batch.Export.image.toDrive(image=image,folder=folder, fileNamePrefix='test0')
image = ee.Image(imageCol.toList(imageCol.size()).get(1))
task = ee.batch.Export.image.toDrive(image=image,folder=folder, fileNamePrefix='test1')
task.start()
task.state
