from osgeo import gdal, gdalnumeric, ogr, osr
import EarthModule
import matplotlib.pyplot as plt
import numpy
import geopy.distance
import time

file1=r"Y:\NED\n26w102\imgn26w102_1.img"

obj1=EarthModule.EarthObj_raster(geofile=file1,field="NED",name="f1")

#plt.imshow(obj1.getData("NED"))

data=obj1.getData("NED")
gradx,grady=numpy.gradient(data)

x1,x2,y1,y2=obj1.getBoundingBox()
dx,dy=obj1.getDxDy()
nx,ny=obj1.getNxNy()
xx=numpy.linspace(x1+dx,x2-dx,nx)
yy=numpy.linspace(y1+dy,y2-dy,ny)

dmx=numpy.zeros([1,ny])
dmy=numpy.zeros([1,ny])
for i in range(ny):
    dmx[0,i]=geopy.distance.vincenty((yy[i],xx[0]),(yy[i],xx[0]+dx)).meters
    dmy[0,i]=geopy.distance.vincenty((yy[i]+dy/2,xx[0]),(yy[i]-dy/2,xx[0])).meters

gradmx=gradx/dmx
gradmy=grady/dmy

sp=numpy.sqrt(gradmx**2+gradmy**2)
slope=numpy.arctan(numpy.sqrt(gradmx**2+gradmy**2))/numpy.pi*180

