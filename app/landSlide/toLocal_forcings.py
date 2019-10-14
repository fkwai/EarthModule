import pandas as pd
import ee
import earthModule
from earthModule.data import landSlide, geeUtils, earthEngine
import datetime
import time
import os
ee.Initialize()

dirDB = r'/mnt/sdb/landSlideDB/'
nBuf = 1000
nDay = 200

saveFolder = os.path.join(
    dirDB, 'conf8', 'PRISM-buffer{:d}-day{:d}'.format(nBuf, nDay))
if not os.path.exists(saveFolder):
    os.makedirs(saveFolder)

latLst, lonLst, dateLst = landSlide.readTabInfo(tabFile=None)
nSite = len(dateLst)
fieldLst = ['ppt','tmean','tdmean']
siteLst = list()

tt0 = time.time()
errLst=list()
for k in range(nSite):
    tt1 = time.time()
    saveName = 'site{:04d}'.format(k)
    point = ee.Geometry.Point(lonLst[k], latLst[k])
    t1 = dateLst[k]-datetime.timedelta(days=nDay)
    t2 = dateLst[k]+datetime.timedelta(days=nDay)
    imageCol = ee.ImageCollection("OREGONSTATE/PRISM/AN81d").filterDate(
        geeUtils.t2ee(t1), geeUtils.t2ee(t2)).filterBounds(point).select(fieldLst).sort('system:time_start')
    region = ee.Geometry.Point(lonLst[k], latLst[k]).buffer(nBuf)
    try:
        df = earthEngine.calRegion(imageCol, fieldLst, region)
        savePath = os.path.join(saveFolder, saveName)
        df.to_json(savePath)
    except:
        errLst.append(k)
        tt = time.time()
        print('\t Site {} time {:.3f} total {:.3f}'.format(
            k, tt-tt1, tt-tt0))