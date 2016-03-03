import os,sys
from osgeo import gdal, gdalnumeric, ogr, osr
import numpy,scipy
from datetime import date
import bisect

print("loading Earth Module")

class daf():
    pass


class EarthObj_raster():
    name=[]
    geoTransform=[]
    geoProjection=[]

    fieldList=[]
    data={}
    time={}

    def __init__(self,name,geofile,field=0,date=0):
        self.name=name
        ds = gdal.Open(geofile)
        self.geoProjection=ds.GetProjection()
        self.geoTransform=ds.GetGeoTransform()

        if field!=0:
            temp = numpy.array(ds.GetRasterBand(1).ReadAsArray())
            self.data[field]=temp
            self.time[field]=[date]
            self.fieldList.append(field)

    def addDataRaster(self,raster,field,date=0,isGRACE=0):
        ds = gdal.Open(raster)

        # check geospatial information here

        temp = numpy.array(ds.GetRasterBand(1).ReadAsArray())

        if isGRACE:
            temp=numpy.concatenate((temp[:,180:360],temp[:,0:180]),axis=1)

        if field in self.fieldList:
            datelist=self.time[field]
            ind=bisect.bisect(datelist,date)
            if self.data[field].ndim==2:
                self.data[field]=self.data[field][:,:,numpy.newaxis]
            datatemp=numpy.insert(self.data[field],ind,temp,axis=2)
            self.data[field]=datatemp
            self.time[field].insert(ind,date)

        else:
            self.data[field]=temp
            self.time[field]=[date]
            self.fieldList.append(field)


class EarthObj_vector():
    name=[]
    ID=[]
    feature=[]
    geometry=[]
    spatialRef=[]
    geometrytype=[]
    nfeature=[]

    field=[]
    data={}
    time={}

    def __init__(self,name,geofile,IDfield):
        self.name=name
        shapef = ogr.Open(geofile)
        layer=shapef.GetLayer(os.path.split(os.path.splitext(geofile)[0])[1])
        self.nfeature = layer.GetFeatureCount()
        self.geometrytype=layer.GetGeomType()
        self.spatialRef=layer.GetSpatialRef()

        for i in range(self.nfeature):
            feature = layer.GetFeature(i)
            geometry=feature.geometry()
            self.feature.append(feature)
            self.geometry.append(geometry)
            self.ID.append(int(feature.GetField(IDfield)))


def writeGRACEReftiff(filename,outRaster):
    # GRACE is from 0 - 360.. write an empty tiff from -180 - 180
    filehandle = gdal.Open(filename)
    band1 = filehandle.GetRasterBand(1)
    geotransform = filehandle.GetGeoTransform()
    geoproj = filehandle.GetProjection()
    data = band1.ReadAsArray()*0

    geotransform=(-180, 1.0, 0.0, 90.0, 0.0, -1.0)

    (x,y) = data.shape
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    dst_datatype = gdal.GDT_Byte
    dst_ds = driver.Create(outRaster,y,x,1,dst_datatype)
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetProjection(geoproj)
