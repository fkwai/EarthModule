
import folium
import ee
import webbrowser

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
    return imageLst


def mapBound(imageCol, bb, nImage=None):
    imageLst = col2lst(imageCol, nImage=None)
    center = [(bb[0]+bb[2])/2, (bb[1]+bb[3])/2]
    bbMap = [bb[0], bb[1]], [bb[2], bb[3]]
    mm = folium.Map(location=center)
    folium.Rectangle(bbMap, color='red',).add_to(mm)
    for k in range(nImage):
        print('working on image '+str(k), end='\r')
        image = ee.Image(imageLst.get(k))
        addToMap(image, mm, bands=[
            'B3', 'B2', 'B1'], min=0, max=1000)
    mm.fit_bounds(bbMap)
    mm.add_child(folium.LayerControl())
    mm.save('map.html')
    webbrowser.open('map.html')


def exportDrive(imageCol, folder, nImage=None):
    taskLst = list()
    imageLst = col2lst(imageCol, nImage=None)
    for k in range(nImage):
        print('working on image '+str(k), end='\r')
        image = ee.Image(imageLst.get(k))
        task = ee.batch.Export.image.toDrive(
            image=image, folder=folder, fileNamePrefix=image.date().format('yyyyMMdd').getInfo())
        task.start()
    return taskLst
