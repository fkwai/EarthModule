import pandas as pd
import ee
import earthModule
from earthModule.data import landSlide, geeUtils
import datetime
import time
import os
ee.Initialize()

dirDB = r'/mnt/sdb/landSlideDB/'

nBuf = 300
nDay = 200
saveFolder = os.path.join(dirDB, 'conf8-buf{:d}-day{:d}'.format(nBuf, nDay))
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
    region = ee.Geometry.Point(lonLst[k], latLst[k]).buffer(nBuf)
    t1 = dateLst[k]-datetime.timedelta(days=nDay)
    t2 = dateLst[k]+datetime.timedelta(days=nDay)

    imageCol = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(
        geeUtils.t2ee(t1), geeUtils.t2ee(t2)).filterBounds(region).select(fieldLst).sort('system:time_start')
    nImage = imageCol.size().getInfo()
    imageLst = imageCol.toList(nImage)
    df = pd.DataFrame(columns=['date']+fieldLst)
    for kk in range(nImage):
        print('\t Total image {} working on {}'.format(nImage, kk), end='\r')
        image = ee.Image(imageLst.get(kk))
        temp = image.reduceRegion(ee.Reducer.mean(), region).getInfo()
        tstr = image.date().format('yyyy-MM-dd').getInfo()
        temp['date'] = tstr
        df=df.append(temp,ignore_index=True)
    df.to_csv(os.path.join(saveFolder, saveName), index=False)
    tt = time.time()
    print('\t Site {} time {:.3f} totle {:.3f}'.format(
        k, tt-tt1, tt-tt0))
