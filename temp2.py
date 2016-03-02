import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

#############################################################################

class MapViewer(QMainWindow):
    def __init__(self, layer):
        QMainWindow.__init__(self)
        self.setWindowTitle("Map Viewer")

        canvas = QgsMapCanvas()
        canvas.useImageToRender(False)
        canvas.setCanvasColor(Qt.white)
        canvas.show()

        QgsMapLayerRegistry.instance().addMapLayer(layer)
        canvas.setExtent(layer.extent())
        canvas.setLayerSet([QgsMapCanvasLayer(layer)])

        layout = QVBoxLayout()
        layout.addWidget(canvas)

        contents = QWidget()
        contents.setLayout(layout)
        self.setCentralWidget(contents)

#############################################################################
def test2():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
    QgsApplication.initQgis()

    shpfile="Y:\\HUCs\\HUC4_main_data.shp"
    tiffile="Y:\\SRTM\\srtm_01_02\\srtm_01_02.tif"

    vlayer = QgsVectorLayer(shpfile, "HUC4", "ogr")

    app.exec_()
    QgsApplication.exitQgis()
    return vlayer

vlayer=test2()

def test():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
    QgsApplication.initQgis()

    shpfile="Y:\\HUCs\\HUC4_main_data.shp"
    tiffile="Y:\\SRTM\\srtm_01_02\\srtm_01_02.tif"

    vlayer = QgsVectorLayer(shpfile, "HUC4", "ogr")
    fileInfo = QFileInfo(tiffile)
    baseName = fileInfo.baseName()
    rlayer = QgsRasterLayer(tiffile, baseName)

    viewer = MapViewer(vlayer)


    viewer.show()

    app.exec_()

    QgsApplication.exitQgis()

    registry = QgsProviderRegistry.instance()
    provider = registry.provider("ogr", "Y:\\HUCs\\HUC4_main_data.shp")

test()