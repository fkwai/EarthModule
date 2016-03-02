
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import EarthModule
import glob
import datetime


app = QApplication(sys.argv)
QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
QgsApplication.initQgis()

shpfile=r"Y:\HUCs\HUC4_main_data_proj.shp"
tiffile=r"Y:\GRACE\geotiff\CLM4.LEAKAGE_ERROR.DS.G300KM.RL05.DSTvSCS1409.tif"
tiffile2=r"Y:\Kuai\HYP_HR_SR_OB_DR\HYP_HR_SR_OB_DR.tif"

vlayer = QgsVectorLayer(shpfile, "HUC4", "ogr")
fileInfo = QFileInfo(tiffile)
baseName = fileInfo.baseName()
rlayer = QgsRasterLayer(tiffile, baseName)

# viewer = EarthModule.Map(rlayer)

app.exec_()
QgsApplication.exitQgis()

HUCobj=EarthModule.EarthObj_vector("HUC4",shpfile,"HUC4")

GRACEobj=EarthModule.EarthObj_raster("GRACE",tiffile)
filelist=glob.glob("Y:\GRACE\geotiff\*CSR*.tif")
i=0
for file in filelist:
    print i
    i=i+1
    filename=os.path.splitext(os.path.basename(file))[0]
    datestr=filename.split(".")[2]
    date=datetime.datetime.strptime(str(datestr),"%Y%m%d").date()
    GRACEobj.addDataRaster(file,"GRACE",date)


from osgeo import gdal, gdalnumeric, ogr, osr
from gdalconst import *
import numpy
ds = gdal.Open(tiffile2)
myarray = numpy.array(ds.GetRasterBand(1).ReadAsArray())

shapef = ogr.Open(shpfile)
lyr = shapef.GetLayer( os.path.split( os.path.splitext( shpfile )[0] )[1] )
poly = lyr.GetNextFeature()
nf = lyr.GetFeatureCount()
for i in range(nf):
    feature = lyr.GetFeature(i)
    print(feature.GetField("HUC4"))
