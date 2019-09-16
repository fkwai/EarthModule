import os,sys
from osgeo import gdal,gdalnumeric,ogr,osr,gdal_array
import numpy,scipy
from datetime import date
import bisect

print("loading Earth Module")

class daf():
    pass


class EarthObj_raster():
    def __init__(self,geofile=None,name=None,field=None,date=0,
                 geoProjection=None,geoTransform=None,data=None,
                 isGRACE=0,optNan=1):
        '''
        init 1: from geofile
        init 2: from geoProjection,geoTransform,data
        option: field(intial input data as field),name, date
        '''

        #initial variables
        self.__data={}
        self.__time={}
        self.__fieldList=[]
        self.__name=name

        self.__name=None
        self.__geoTransform=None
        self.__geoProjection=None
        self.__nx=None
        self.__ny=None

        if geofile is not None:
            ds = gdal.Open(geofile)
            self.__geoProjection=ds.GetProjection()
            self.__geoTransform=ds.GetGeoTransform()
            # self.RasterXSize=ds.RasterXSize   so dangerous!!!
            # self.RasterYSize=ds.RasterYSize
            if optNan==0:
                temp = numpy.array(ds.GetRasterBand(1).ReadAsArray())
            else:
                temp = numpy.array(ds.GetRasterBand(1).ReadAsArray()).astype(float)
                nanvalue=ds.GetRasterBand(1).GetNoDataValue()
                temp[numpy.where(temp==nanvalue)]=numpy.nan
        elif (geoProjection is not None) \
                and (geoTransform is not None) \
                and (data is not None):
            self.__geoProjection=geoProjection
            self.__geoTransform=geoTransform
            temp=data[:]
        if field is not None:    # input raster data in initialization
            ny,nx=temp.shape
            self.__nx=nx
            self.__ny=ny
            self.addData(temp,field,date,isGRACE)

    def addDataRaster(self,raster,field,date=0,isGRACE=0):
        ds = gdal.Open(raster)
        # check geospatial information here
        temp = numpy.array(ds.GetRasterBand(1).ReadAsArray()).astype(float)
        nanvalue=ds.GetRasterBand(1).GetNoDataValue()
        temp[numpy.where(temp==nanvalue)]=numpy.nan
        self.addData(self,temp,field,date,isGRACE)


    def addData(self,data,field,date=0,isGRACE=0):
        if isGRACE:
            data=numpy.concatenate((data[:,180:360],data[:,0:180]),axis=1)
        if field in self.__fieldList:
            datelist=self.__time[field]
            ind=bisect.bisect(datelist,date)
            if self.__data[field].ndim==2:
                self.__data[field]=self.__data[field][:,:,numpy.newaxis]
            datatemp=numpy.insert(self.__data[field],ind,data,axis=2)
            self.__data[field]=datatemp
            self.__time[field].insert(ind,date)
        else:
            self.__data[field]=data
            self.__time[field]=[date]
            self.__fieldList.append(field)

    def getData(self,field=None,date=0):
        if field is None:
            return self.__data
        else:
            return self.__data[field]
            # use date later

    def getTime(self,field=None):
        if field is None:
            return self.__time
        else:
            return self.__time[field]

    def getProjection(self):
        return self.__geoProjection

    def getGeoTransform(self):
        return self.__geoTransform

    def writeTiff(self,outfile,field,wopt=0):
        if self.__data[field].ndim==2:
            data=self.__data[field]
        (x,y) = data.shape
        format = "GTiff"
        driver = gdal.GetDriverByName(format)
        dst_datatype=gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype.type)
        dst_ds = driver.Create(outfile,y,x,1,dst_datatype)
        dst_ds.GetRasterBand(1).WriteArray(data)
        dst_ds.GetRasterBand(1).ComputeStatistics(False)
        dst_ds.SetGeoTransform(self.__geoTransform)
        dst_ds.SetProjection(self.__geoProjection)

    def getBoundingBox(self):
        # (x1,y1): up-left; (x2,y2):bottom-right
        x1 = self.__geoTransform[0]
        y1 = self.__geoTransform[3]
        x2 = self.__geoTransform[0]+self.__geoTransform[1]*self.__nx
        y2 = self.__geoTransform[3]+self.__geoTransform[5]*self.__ny
        return x1,x2,y1,y2

    def getDxDy(self):
        dx = self.__geoTransform[1]
        dy = self.__geoTransform[5]
        return dx,dy

    def getNxNy(self):
        nx = self.__nx
        ny = self.__ny
        return nx,ny


class EarthObj_vector():
    def __init__(self,geofile=None,IDfield=None,name=None):
        # initial variables
        self.__data={}
        self.__time={}
        self.__fieldList=[]
        self.__name=name

        self.__ID=[]
        self.__feature=[]
        self.__geometry=[]
        self.__spatialRef=None
        self.__geometrytype=None
        self.__nfeature=None

        shapef = ogr.Open(geofile)
        layer=shapef.GetLayer(os.path.split(os.path.splitext(geofile)[0])[1])
        self.__nfeature = layer.GetFeatureCount()
        self.__geometrytype=layer.GetGeomType()
        self.__spatialRef=layer.GetSpatialRef()
        for i in range(self.__nfeature):
            feature = layer.GetFeature(i)
            geometry=feature.geometry()
            self.__feature.append(feature)
            self.__geometry.append(geometry)
            self.__ID.append(int(feature.GetField(IDfield)))

    def getData(self,field=None):
        if field is None:
            return self.__data
        else:
            return self.__data[field]

    def getTime(self,field=None):
        if field is None:
            return self.__time
        else:
            return self.__time[field]
    def getID(self):
        return self.__ID
    def getSpatialRef(self):
        return self.__spatialRef
    def getGeometry(self):
        return self.__geometry
    def getFeature(self):
        return self.__feature

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
