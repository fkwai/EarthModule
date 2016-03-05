from osgeo import gdal, gdalnumeric, ogr, osr
import Image, ImageDraw
import numpy
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

def clip(poly,geoTrans,srcArray):
    minX, maxX, minY, maxY = poly.GetEnvelope()
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)

    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)

    cliplocal = srcArray[ulY:lrY, ulX:lrX]

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
    masklocal = imageToArray(rasterPoly)

    cliplocal = gdalnumeric.choose(masklocal,(cliplocal, 0))

    clip=numpy.zeros(srcArray.shape)*float("nan")
    mask=numpy.zeros(srcArray.shape)*float("nan")
    clip[ulY:lrY, ulX:lrX]=cliplocal
    mask[ulY:lrY, ulX:lrX]=masklocal

    gdal.ErrorReset()

    return clip,mask
