from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class EarthObj_vector(object):
    name=[]
    def __init__(self,name,geofile):
        self.name=name

class EarthObj_vector(object):
    name=[]
    ID=[]
    def __init__(self,name,geofile):
        self.name=name
        vlayer = QgsVectorLayer(geofile,name,"ogr")



class Map(QMainWindow):
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