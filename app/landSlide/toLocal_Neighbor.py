import pandas as pd
import ee
import earthModule
from earthModule.data import landSlide, geeUtils, earthEngine
import datetime
import time
import os
ee.Initialize()

dirDB = r'/mnt/sdb/landSlideDB/'
nKernel = 9
nDay = 200

saveFolder = os.path.join(
    dirDB, 'conf8-kernal{:d}-day{:d}'.format(nKernel, nDay))
if not os.path.exists(saveFolder):
    os.makedirs(saveFolder)


latLst, lonLst, dateLst = landSlide.readTabInfo(tabFile=None)
nSite = len(dateLst)
fieldLst = ['B'+str(x+1) for x in range(7)]
fieldLst.append('pixel_qa')
siteLst = list()

tt0 = time.time()
for k in range(nSite):
    tt1 = time.time()
    saveName = 'site{:04d}'.format(k)
    point = ee.Geometry.Point(lonLst[k], latLst[k])
    t1 = dateLst[k]-datetime.timedelta(days=nDay)
    t2 = dateLst[k]+datetime.timedelta(days=nDay)

    imageCol = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(
        geeUtils.t2ee(t1), geeUtils.t2ee(t2)).filterBounds(point).select(fieldLst).sort('system:time_start')
    df = earthEngine.calNeighbor(imageCol, fieldLst, point, kSize=nKernel)
    savePath = os.path.join(saveFolder, saveName)
    df.to_json(savePath)
    tt = time.time()
    print('\t Site {} time {:.3f} total {:.3f}'.format(
        k, tt-tt1, tt-tt0))
