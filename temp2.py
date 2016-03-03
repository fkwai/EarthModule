from osgeo import gdal, gdalnumeric, ogr, osr
import Image, ImageDraw
import numpy
import EarthModule
gdal.UseExceptions()


def imageToArray(i):
    a=gdalnumeric.fromstring(i.tostring(),'b')
    a.shape=i.im.size[1], i.im.size[0]
    return a

def arrayToImage(a):
    i=Image.fromstring('L',(a.shape[1],a.shape[0]),
            (a.astype('b')).tostring())
    return i

def world2Pixel(geoMatrix, x, y):
  ulX = geoMatrix[0]
  ulY = geoMatrix[3]
  xDist = geoMatrix[1]
  yDist = geoMatrix[5]
  rtnX = geoMatrix[2]
  rtnY = geoMatrix[4]
  pixel = int((x - ulX) / xDist)
  line = int((ulY - y) / xDist)
  return (pixel, line)

raster_path=r"Y:\GRACE\geotiff\CLM4.LEAKAGE_ERROR.DS.G300KM.RL05.DSTvSCS1409.tif"
shapefile_path=r"Y:\HUCs\HUC4_main_data_proj.shp"

shpfile=r"Y:\HUCs\HUC4_main_data_proj.shp"
vectorObj=EarthModule.EarthObj_vector("HUC4",shpfile,"HUC4")

tiffile=r"Y:\SRTM\srtm_19_06\srtm_19_06.tif"
rasterObj=EarthModule.EarthObj_raster("SRTM",tiffile,field="DEM")

geoTrans = rasterObj.geoTransform
srcArray = rasterObj.data["DEM"]
poly=vectorObj.geometry[2]

minX, maxX, minY, maxY = poly.GetEnvelope()
ulX, ulY = world2Pixel(geoTrans, minX, maxY)
lrX, lrY = world2Pixel(geoTrans, maxX, minY)

pxWidth = int(lrX - ulX)
pxHeight = int(lrY - ulY)

clip = srcArray[ulY:lrY, ulX:lrX]

geoTrans = list(geoTrans)
geoTrans[0] = minX
geoTrans[3] = maxY

points = []
pixels = []
pts = poly.GetGeometryRef(0)
for p in range(pts.GetPointCount()):
    points.append((pts.GetX(p), pts.GetY(p)))
for p in points:
    pixels.append(world2Pixel(geoTrans, p[0], p[1]))
rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
rasterize = ImageDraw.Draw(rasterPoly)
rasterize.polygon(pixels, 0)
mask = imageToArray(rasterPoly)

# Clip the image using the mask
clip = gdalnumeric.choose(mask,(clip, 0))

output=numpy.zeros(srcArray.shape)*float("nan")
output[ulY:lrY, ulX:lrX]=clip

gdal.ErrorReset()