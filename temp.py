import gdal,ogr,fiona
import os
import matplotlib.pyplot as plt
GISFile="Y:\\HUCs\\HUC4_main_data.shp"
GISFile="Y:\SRTM\srtm_01_07\strm_01_07.tif"

driver = ogr.GetDriverByName('ESRI Shapefile')
dataSource = driver.Open(GISFile, 0) # 0 means read-only. 1 means writeable.
layer = dataSource.GetLayer()
feat=layer.GetFeature(0)
geo=feat.geometry()
geom = geo.GetGeometryRef(0)

import fiona
GISFile="Y:\\HUCs\\HUC4_main_data.shp"
a=fiona.open(GISFile)

import EarthModule
reload(EarthModule)
HUCshp="Y:\\HUCs\\HUC4_main_data.shp"
HUCobj=EarthModule.EarthObj(name="HUC4",GISFile=HUCshp,IDfield="HUC4")