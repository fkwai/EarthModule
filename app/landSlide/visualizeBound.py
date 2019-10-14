import tensorflow as tf
import ee
import folium
import webbrowser
import earthModule
from earthModule.data import landSlide, geeUtils, earthEngine

fileNamePre = 'GE_39.667262_-105.280804_39.667973_-105.279188_20121007_PRE'
fileNamePost = 'GE_39.667262_-105.280804_39.667973_-105.279188_20131006_POST'

bb = landSlide.readFileBound(fileNamePre)
t1 = landSlide.readFileDate(fileNamePre)
t2 = landSlide.readFileDate(fileNamePost)


def mapFunc(image):
    return image.clip(geeUtils.bb2ee(bb))


imageCol = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(
    geeUtils.t2ee(t1), geeUtils.t2ee(t2)).filterBounds(
        geeUtils.bb2ee(bb)).select('B[1-7]').sort('system:time_start')

earthEngine.mapBound(imageCol, bb, bands=[
    'B3', 'B2', 'B1'], min=0, max=1000)
