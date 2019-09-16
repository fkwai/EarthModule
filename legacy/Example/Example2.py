
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import EMGIS

shpfile=r"Y:\HUCs\HUC4_main_data_proj.shp"
tiffile=r"Y:\GRACE\geotiff\CLM4.LEAKAGE_ERROR.DS.G300KM.RL05.DSTvSCS1409.tif"

app = QApplication(sys.argv)
QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
QgsApplication.initQgis()

vlayer = QgsVectorLayer(shpfile, "HUC4", "ogr")
fileInfo = QFileInfo(tiffile)
baseName = fileInfo.baseName()
rlayer = QgsRasterLayer(tiffile, baseName)

window = EMGIS.MapExplorer()
window.show()
window.raise_()
window.loadMap(vlayer)
window.setPanMode()

app.exec_()
app.deleteLater()
QgsApplication.exitQgis()


