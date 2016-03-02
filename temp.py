import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import EarthModule

shpfile="Y:\\HUCs\\HUC4_main_data_proj.shp"
tiffile="Y:\\SRTM\\srtm_01_02\\srtm_01_02.tif"

vlayer = QgsVectorLayer(shpfile, "HUC4", "ogr")
fileInfo = QFileInfo(tiffile)
baseName = fileInfo.baseName()
rlayer = QgsRasterLayer(tiffile, baseName)

app = QApplication(sys.argv)
QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
QgsApplication.initQgis()

viewer = EarthModule.Map(rlayer)


app.exec_()
QgsApplication.exitQgis()

import scipy.io as sio
matfile=r"Y:\DataAnaly\BasinStr\HUCstr_new.mat"
mat = sio.loadmat(matfile)

hucstr=mat["HUCstr"]