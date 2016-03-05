from osgeo import gdal, gdalnumeric, ogr, osr
from EarthModule import *
import gdal_merge
import numpy
import matplotlib.pyplot as plt

file1=r"Y:\NED\n24w107\imgn24w107_1.img"
file2=r"Y:\NED\n25w107\imgn25w107_1.img"
file3=r"Y:\NED\n24w106\imgn24w106_1.img"
fileList=[file1,file2,file3]

obj1=EarthObj_raster(geofile=file1,field="NED")
obj2=EarthObj_raster(geofile=file2,field="NED")
obj3=EarthObj_raster(geofile=file3,field="NED")

plt.imshow(obj1.getData("NED"))

objList=[obj1,obj2,obj3]

x1t,x2t,y1t,y2t=objList[0].getBoundingBox()
x1,x2,y1,y2=x1t,x2t,y1t,y2t
for obj in objList:
    x1t,x2t,y1t,y2t=obj.getBoundingBox()
    x1 = min(x1,x1t)
    y1 = max(y1,y1t)
    x2 = max(x2,x2t)
    y2 = min(y2,y2t)
dx,dy=objList[0].getDxDy()
geotransform=[x1,dx,0,y1,0,dy]
projection=obj1.getProjection()

nx=int(numpy.ceil((x2-x1)/dx))
ny=int(numpy.ceil((y2-y1)/dy))

dataMerge=numpy.zeros([ny,nx])*numpy.nan
for obj in objList:
    x1t,x2t,y1t,y2t=obj.getBoundingBox()
    indx1=int(numpy.round((x1t-x1)/dx))
    indx2=int(numpy.round((x2t-x1)/dx))
    indy1=int(numpy.round((y1t-y1)/dy))
    indy2=int(numpy.round((y2t-y1)/dy))
    data=None
    data=obj.getData(field="NED")[:]

    dataMerge[indy1:indy2,indx1:indx2]=data

objMerge=EarthModule.EarthObj_raster(field="NED",geoProjection=projection,
                                     geoTransform=geotransform,data=dataMerge)
objMerge.writeTiff(outfile="out5.tif",field="NED")



