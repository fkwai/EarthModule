from osgeo import gdal, gdalnumeric, ogr, osr
import Image, ImageDraw
import numpy
import EarthModule
import geopy.distance
import csv
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
  pixel = int((x - ulX)/xDist)
  line = int((y-ulY)/yDist)
  return (pixel, line)

def clip(poly,rasterObj,field,date=0,vNan=numpy.nan):
    '''
    :param poly:geometry in vectorObj
    :param rasterObj: rasterObj to clip
    :param field: rasterObj clip field
    :return: clip rasterObj and mask rasterObj
    '''

    rasterGeoTrans=rasterObj.getGeoTransform()
    rasterProjection=rasterObj.getProjection()
    rasterArray=rasterObj.getData(field=field,date=date)

    minX, maxX, minY, maxY = poly.GetEnvelope()
    indx1, indy1 = world2Pixel(rasterGeoTrans, minX, maxY)
    indx2, indy2 = world2Pixel(rasterGeoTrans, maxX, minY)

    pxWidth = int(indx2 - indx1)
    pxHeight = int(indy2 - indy1)

    clip = rasterArray[indy1:indy2, indx1:indx2]

    geoTrans = list(rasterGeoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY

    mask=None
    if poly.GetGeometryType()==6:
        for polygon in poly:
            points = []
            pixels = []
            pts = polygon.GetGeometryRef(0)
            for p in range(pts.GetPointCount()):
                points.append((pts.GetX(p), pts.GetY(p)))
            for p in points:
                pixels.append(world2Pixel(geoTrans, p[0], p[1]))
            rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
            rasterize = ImageDraw.Draw(rasterPoly)
            rasterize.polygon(pixels, 0)
            if mask is None:
                mask = imageToArray(rasterPoly)
            else:
                masktemp = imageToArray(rasterPoly)
                mask=mask*masktemp
    elif poly.GetGeometryType()==3:
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

    clip = gdalnumeric.choose(mask,(clip, vNan))

    dx=rasterGeoTrans[1]
    dy=rasterGeoTrans[5]
    x1=rasterGeoTrans[0]+dx*indx1
    y1=rasterGeoTrans[3]+dy*indy1
    clipGeoTrans=(x1,dx,0.0,y1,0.0,dy)

    gdal.ErrorReset()
    clipObj=EarthModule.EarthObj_raster(field=field,geoProjection=rasterProjection,
                                     geoTransform=clipGeoTrans,data=clip)
    maskObj=EarthModule.EarthObj_raster(field=field,geoProjection=rasterProjection,
                                     geoTransform=clipGeoTrans,data=mask)

    return clipObj,maskObj

def merge(rasterObjList,field,date=0):
    x1t,x2t,y1t,y2t=rasterObjList[0].getBoundingBox()
    x1,x2,y1,y2=x1t,x2t,y1t,y2t
    for obj in rasterObjList:
        x1t,x2t,y1t,y2t=obj.getBoundingBox()
        x1 = min(x1,x1t)
        y1 = max(y1,y1t)
        x2 = max(x2,x2t)
        y2 = min(y2,y2t)
    dx,dy=rasterObjList[0].getDxDy()
    geotransform=[x1,dx,0,y1,0,dy]
    projection=rasterObjList[0].getProjection()

    nx=int(numpy.ceil((x2-x1)/dx))
    ny=int(numpy.ceil((y2-y1)/dy))

    dataMerge=numpy.zeros([ny,nx])*numpy.nan
    for obj in rasterObjList:
        x1t,x2t,y1t,y2t=obj.getBoundingBox()
        indx1=int(numpy.round((x1t-x1)/dx))
        indx2=int(numpy.round((x2t-x1)/dx))
        indy1=int(numpy.round((y1t-y1)/dy))
        indy2=int(numpy.round((y2t-y1)/dy))
        data=None
        data=obj.getData(field=field,date=date)[:]

        dataMerge[indy1:indy2,indx1:indx2]=data

    objMerge=EarthModule.EarthObj_raster(field=field,geoProjection=projection,
                                         geoTransform=geotransform,data=dataMerge)
    return objMerge

def slope(rasterObj,field):
    data=rasterObj.getData(field)
    gradx,grady=numpy.gradient(data)

    x1,x2,y1,y2=rasterObj.getBoundingBox()
    dx,dy=rasterObj.getDxDy()
    nx,ny=rasterObj.getNxNy()
    xx=numpy.linspace(x1+dx,x2-dx,nx)
    yy=numpy.linspace(y1+dy,y2-dy,ny)

    dmx=numpy.zeros([ny,1])
    dmy=numpy.zeros([ny,1])
    for i in range(ny):
        dmx[i,0]=geopy.distance.vincenty((yy[i],xx[0]),(yy[i],xx[0]+dx)).meters
        dmy[i,0]=geopy.distance.vincenty((yy[i]+dy/2,xx[0]),(yy[i]-dy/2,xx[0])).meters

    gradmx=gradx/dmx
    gradmy=grady/dmy

    sp=numpy.sqrt(gradmx**2+gradmy**2)
    slope=numpy.arctan(numpy.sqrt(gradmx**2+gradmy**2))/numpy.pi*180
    return slope

def writeCSV(csvfile,data):
    '''
    :param csvfile: csv file to write
    :param data: list of list
    :return:
    '''
    fout=open(csvfile,"wb")
    csvout=csv.writer(fout)
    csvout.writerows(zip(*data))
    fout.close()