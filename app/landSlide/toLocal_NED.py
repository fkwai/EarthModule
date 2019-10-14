import pandas as pd
import ee
import earthModule
from earthModule.data import landSlide, geeUtils, earthEngine
import datetime
import time
import os
import json

ee.Initialize()

# hyper-parameters

dirDB = r'/home/kxf227/work/GitHUB/earthModule/app/landSlide/data/'
kSize = 9
saveFolder = os.path.join(
    dirDB, 'conf8', 'const')
if not os.path.exists(saveFolder):
    os.makedirs(saveFolder)

# init
latLst, lonLst, dateLst = landSlide.readTabInfo(tabFile=None)
nSite = len(dateLst)


dataset = ee.Image('USGS/NED')
ned = dataset.select('elevation')
tt0 = time.time()
errLst = list()
for k in range(nSite):
    tt1 = time.time()
    try:
        point = ee.Geometry.Point(lonLst[k], latLst[k])
        lst = ee.List.repeat(1, kSize)
        lists = ee.List.repeat(lst, kSize)
        kernel = ee.Kernel.fixed(kSize, kSize, lists)
        imageArray = ned.neighborhoodToArray(kernel).reduceRegion(ee.Reducer.first(), point, 30).getInfo()
        dictOut = dict()
        dictOut['NED-kernel{:d}'.format(kSize)] = imageArray['elevation']
        saveName = 'site{:04d}'.format(k)
        savePath = os.path.join(saveFolder, saveName)
        with open(savePath, 'w') as json_file:
            json.dump(dictOut, json_file)
    except:
        errLst.append(k)
        print(k)    
    tt = time.time()
    print('\t Site {} time {:.3f} total {:.3f}'.format(k, tt-tt1, tt-tt0))
