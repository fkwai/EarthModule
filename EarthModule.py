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
    dataset_GDAL=[]

    fieldList=[]
    data={}
    time={}

    def __init__(self,name,geofile):
        self.name=name
        self.dataset_GDAL = gdal.Open(geofile)

    def addDataRaster(self,raster,field,date=0):
        ds = gdal.Open(raster)

        # check geospatial information here

        temp = numpy.array(ds.GetRasterBand(1).ReadAsArray())
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
    layer_OGR=[]
    geomtype=[]
    nfeature=[]

    field=[]
    data={}
    time={}

    def __init__(self,name,geofile,IDfield):
        self.name=name
        shapef = ogr.Open(geofile)
        layer=shapef.GetLayer(os.path.split(os.path.splitext(geofile)[0])[1])
        self.layer_OGR=layer
        self.nfeature = layer.GetFeatureCount()
        self.geomtype=layer.GetGeomType()

        for i in range(self.nfeature):
            feature = layer.GetFeature(i)
            self.ID.append(feature.GetField(IDfield))
