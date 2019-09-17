import tensorflow as tf
import ee
import folium
import webbrowser
import earthModule
from earthModule.data import landSlide
# import .landSlide

fileNamePre='GE_39.667262_-105.280804_39.667973_-105.279188_20121007_PRE'
fileNamePost='GE_39.667262_-105.280804_39.667973_-105.279188_20131006_POST'

bb, t1=landSlide.readFileInfo(fileNamePre)
bb, t2=landSlide.readFileInfo(fileNamePost)

dataset = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(t1,t2).filterBounds(bb).select('B[1-7]')