
import folium
import ee
import webbrowser
import time
import pandas as pd

EE_TILES = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}'


def addToMap(image, mm, **kw):
    mapid = image.getMapId(kw)
    folium.TileLayer(
        tiles=EE_TILES.format(**mapid),
        attr='Google Earth Engine',
        overlay=True,
        name=image.date().format('yyyyMMdd').getInfo(),
    ).add_to(mm)


def col2lst(imageCol, nImage=None):
    if nImage is None:
        nImage = imageCol.size().getInfo()
    imageLst = imageCol.toList(nImage)
    return imageLst, nImage


def mapBound(imageCol, bb, nImage=None, **kw):
    imageLst = col2lst(imageCol, nImage=None)
    center = [(bb[0]+bb[2])/2, (bb[1]+bb[3])/2]
    bbMap = [bb[0], bb[1]], [bb[2], bb[3]]
    mm = folium.Map(location=center)
    folium.Rectangle(bbMap, color='red',).add_to(mm)
    for k in range(nImage):
        print('\t working on image '+str(k), end='\r')
        image = ee.Image(imageLst.get(k))
        addToMap(image, mm)
    mm.fit_bounds(bbMap)
    mm.add_child(folium.LayerControl())
    mm.save('map.html')
    webbrowser.open('map.html')


def exportDrive(imageCol, folder, nImage=None):
    taskLst = list()
    imageLst, nImage = col2lst(imageCol, nImage=None)
    for k in range(nImage):
        print('\t working on image '+str(k), end='\r')
        image = ee.Image(imageLst.get(k))
        task = ee.batch.Export.image.toCloudStorage(
            image=image, bucket='deepldb',
            fileNamePrefix=folder+'/'+image.date().format('yyyyMMdd').getInfo()
        )
        task.start()
    return taskLst


def calRegion(imageCol, fieldLst, region, nImage=None):
    imageLst = col2lst(imageCol, nImage=None)
    df = pd.DataFrame(columns=['date']+fieldLst)
    for kk in range(nImage):
        print('\t Total image {} working on {}'.format(nImage, kk), end='\r')
        image = ee.Image(imageLst.get(kk))
        temp = image.reduceRegion(ee.Reducer.mean(), region).getInfo()
        tstr = image.date().format('yyyy-MM-dd').getInfo()
        temp['date'] = tstr
        df = df.append(temp, ignore_index=True)
    return df


def calNeighbor(imageCol, fieldLst, point, scale=30, kSize=9):
    def mapFunc(image):
        lst = ee.List.repeat(1, kSize)
        lists = ee.List.repeat(lst, kSize)
        kernel = ee.Kernel.fixed(kSize, kSize, lists)
        return image.neighborhoodToArray(kernel)

    imageColArray = imageCol.map(mapFunc)
    imageLst = imageColArray.getRegion(point, scale)
    x = imageLst.getInfo()
    out = [dict(zip(x[0], values)) for values in x[1:]]
    df = pd.DataFrame(out)
    df['date'] = df['id'].str[-8:].astype(int)
    return df[fieldLst+['date']]
