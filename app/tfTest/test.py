import pandas as pd
import ee
import earthModule
from earthModule.data import landSlide, geeUtils, earthEngine
import datetime
import time
import os
ee.Initialize()

latLst, lonLst, dateLst = landSlide.readTabInfo(tabFile=None)
nSite = len(dateLst)
fieldLst = ['B'+str(x+1) for x in range(7)]
fieldLst.append('pixel_qa')
siteLst = list()


# for k in range(nSite):
k = 0


saveName = 'site{:04d}'.format(k)
region = ee.Geometry.Point(lonLst[k], latLst[k])
nDay = 100
t1 = dateLst[k]-datetime.timedelta(days=nDay)
t2 = dateLst[k]+datetime.timedelta(days=nDay)

imgCol = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(
    geeUtils.t2ee(t1), geeUtils.t2ee(t2)).filterBounds(region).select(fieldLst).sort('system:time_start')

def mapFunc(image):
    kSize=500
    lst = ee.List.repeat(1, kSize)
    lists = ee.List.repeat(lst, kSize)
    kernel = ee.Kernel.fixed(kSize, kSize, lists)
    return image.neighborhoodToArray(kernel)

tt0=time.time()
imgColArray = imgCol.map(mapFunc)
imgLst = imgColArray.getRegion(region, 10)
x2 = imgLst.getInfo()
out2 = [dict(zip(x2[0], values)) for values in x2[1:]]
df = pd.DataFrame(out2)
print(time.time()-tt0)

