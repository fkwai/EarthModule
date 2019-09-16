from PyQt4 import QtGui, QtCore

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import os

class Ui_ExplorerWindow(object):
    def setupUi(self, window):
        window.setWindowTitle("Kuai's Explorer")

        self.centralWidget = QtGui.QWidget(window)
        self.centralWidget.setMinimumSize(800, 400)
        window.setCentralWidget(self.centralWidget)

        self.menubar = window.menuBar()
        self.fileMenu = self.menubar.addMenu("File")
        self.viewMenu = self.menubar.addMenu("View")
        self.modeMenu = self.menubar.addMenu("Mode")

        self.toolBar = QtGui.QToolBar(window)
        window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.actionQuit = QtGui.QAction("Quit", window)
        self.actionQuit.setShortcut(QtGui.QKeySequence.Quit)

        self.actionShowBasemapLayer = QtGui.QAction("Basemap", window)
        self.actionShowBasemapLayer.setShortcut("Ctrl+B")
        self.actionShowBasemapLayer.setCheckable(True)

        self.actionShowLandmarkLayer = QtGui.QAction("Landmarks", window)
        self.actionShowLandmarkLayer.setShortcut("Ctrl+L")
        self.actionShowLandmarkLayer.setCheckable(True)

        icon = QtGui.QIcon(":/icons/mActionZoomIn.png")
        self.actionZoomIn = QtGui.QAction(icon, "Zoom In", window)
        self.actionZoomIn.setShortcut(QtGui.QKeySequence.ZoomIn)

        icon = QtGui.QIcon(":/icons/mActionZoomOut.png")
        self.actionZoomOut = QtGui.QAction(icon, "Zoom Out", window)
        self.actionZoomOut.setShortcut(QtGui.QKeySequence.ZoomOut)

        icon = QtGui.QIcon(":/icons/mActionPan.png")
        self.actionPan = QtGui.QAction(icon, "Pan", window)
        self.actionPan.setShortcut("Ctrl+1")
        self.actionPan.setCheckable(True)

        icon = QtGui.QIcon(":/icons/mActionExplore.png")
        self.actionExplore = QtGui.QAction(icon, "Explore", window)
        self.actionExplore.setShortcut("Ctrl+2")
        self.actionExplore.setCheckable(True)

        self.fileMenu.addAction(self.actionQuit)

        self.viewMenu.addAction(self.actionShowBasemapLayer)
        self.viewMenu.addAction(self.actionShowLandmarkLayer)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.actionZoomIn)
        self.viewMenu.addAction(self.actionZoomOut)

        self.modeMenu.addAction(self.actionPan)
        self.modeMenu.addAction(self.actionExplore)

        self.toolBar.addAction(self.actionZoomIn)
        self.toolBar.addAction(self.actionZoomOut)
        self.toolBar.addAction(self.actionPan)
        self.toolBar.addAction(self.actionExplore)

        window.resize(window.sizeHint())


class MapExplorer(QMainWindow, Ui_ExplorerWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setupUi(self)

        # self.connect(self.actionQuit, SIGNAL("triggered()"),
        #              qApp.quit)
        self.connect(self.actionShowBasemapLayer, SIGNAL("triggered()"),
                     self.showBasemapLayer)
        self.connect(self.actionShowLandmarkLayer, SIGNAL("triggered()"),
                     self.showLandmarkLayer)
        self.connect(self.actionZoomIn, SIGNAL("triggered()"),
                     self.zoomIn)
        self.connect(self.actionZoomOut, SIGNAL("triggered()"),
                     self.zoomOut)
        self.connect(self.actionPan, SIGNAL("triggered()"),
                     self.setPanMode)
        self.connect(self.actionExplore, SIGNAL("triggered()"),
                     self.setExploreMode)

        self.mapCanvas = QgsMapCanvas()
        self.mapCanvas.useImageToRender(False)
        self.mapCanvas.setCanvasColor(Qt.white)
        self.mapCanvas.show()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mapCanvas)
        self.centralWidget.setLayout(layout)

        self.panTool = PanTool(self.mapCanvas)
        self.panTool.setAction(self.actionPan)

        self.exploreTool = ExploreTool(self)
        self.exploreTool.setAction(self.actionExplore)

        self.actionShowBasemapLayer.setChecked(True)
        self.actionShowLandmarkLayer.setChecked(True)


    def loadMap(self,layer):
        # cur_dir = os.path.dirname(os.path.realpath(__file__))
        # filename = os.path.join(cur_dir, "data",
        #                         "NE1_HR_LC_SR_W_DR",
        #                         "NE1_HR_LC_SR_W_DR.tif")
        # self.basemap_layer = QgsRasterLayer(filename, "basemap")
        # QgsMapLayerRegistry.instance().addMapLayer(self.basemap_layer)
        #
        # filename = os.path.join(cur_dir, "data",
        #                         "ne_10m_populated_places",
        #                         "ne_10m_populated_places.shp")
        # self.landmark_layer = QgsVectorLayer(filename, "landmarks", "ogr")

        self.landmark_layer = layer
        QgsMapLayerRegistry.instance().addMapLayer(self.landmark_layer)

        symbol = QgsSymbolV2.defaultSymbol(self.landmark_layer.geometryType())
        renderer = QgsRuleBasedRendererV2(symbol)
        # root_rule = renderer.rootRule()
        # default_rule = root_rule.children()[0]
        #
        # rule = default_rule.clone()
        # rule.setFilterExpression("(SCALERANK >= 0) and (SCALERANK <= 1)")
        # rule.setScaleMinDenom(0)
        # rule.setScaleMaxDenom(99999999)
        # root_rule.appendChild(rule)
        #
        # rule = default_rule.clone()
        # rule.setFilterExpression("(SCALERANK >= 2) and (SCALERANK <= 4)")
        # rule.setScaleMinDenom(0)
        # rule.setScaleMaxDenom(10000000)
        # root_rule.appendChild(rule)
        #
        # rule = default_rule.clone()
        # rule.setFilterExpression("(SCALERANK >= 5) and (SCALERANK <= 7)")
        # rule.setScaleMinDenom(0)
        # rule.setScaleMaxDenom(5000000)
        # root_rule.appendChild(rule)
        #
        # rule = default_rule.clone()
        # rule.setFilterExpression("(SCALERANK >= 7) and (SCALERANK <= 10)")
        # rule.setScaleMinDenom(0)
        # rule.setScaleMaxDenom(2000000)
        # root_rule.appendChild(rule)
        #
        # root_rule.removeChildAt(0)
        self.landmark_layer.setRendererV2(renderer)

        # p = QgsPalLayerSettings()
        # p.readFromLayer(self.landmark_layer)
        # p.enabled = True
        # p.fieldName = "NAME"
        # p.placement = QgsPalLayerSettings.OverPoint
        # p.displayAll = True
        # expr = ('CASE WHEN SCALERANK IN (0,1) THEN 18 ' +
        #         'WHEN SCALERANK IN (2, 3, 4) THEN 14 ' +
        #         'WHEN SCALERANK IN (5, 6, 7) THEN 12 ' +
        #         'WHEN SCALERANK IN (8, 9, 10) THEN 10 ' +
        #         'ELSE 9 END')
        # p.setDataDefinedProperty(QgsPalLayerSettings.Size, True,
        #                          True, expr, '')
        # p.quadOffset = QgsPalLayerSettings.QuadrantBelow
        # p.yOffset = 1
        # p.labelOffsetInMapUnits = False
        # p.writeToLayer(self.landmark_layer)

        labelingEngine = QgsPalLabeling()
        self.mapCanvas.mapRenderer().setLabelingEngine(labelingEngine)

        self.showVisibleMapLayers()
        self.mapCanvas.setExtent(QgsRectangle(-127.7, 24.4, -79.3, 49.1))


    def showVisibleMapLayers(self):
        layers = []
        if self.actionShowLandmarkLayer.isChecked():
            layers.append(QgsMapCanvasLayer(self.landmark_layer))
        # if self.actionShowBasemapLayer.isChecked():
        #     layers.append(QgsMapCanvasLayer(self.basemap_layer))
        self.mapCanvas.setLayerSet(layers)


    def showBasemapLayer(self):
        self.showVisibleMapLayers()


    def showLandmarkLayer(self):
        self.showVisibleMapLayers()


    def zoomIn(self):
        self.mapCanvas.zoomIn()


    def zoomOut(self):
        self.mapCanvas.zoomOut()


    def setPanMode(self):
        self.actionPan.setChecked(True)
        self.actionExplore.setChecked(False)
        self.mapCanvas.setMapTool(self.panTool)


    def setExploreMode(self):
        self.actionPan.setChecked(False)
        self.actionExplore.setChecked(True)
        self.mapCanvas.setMapTool(self.exploreTool)

#############################################################################

class ExploreTool(QgsMapToolIdentify):
    def __init__(self, window):
        QgsMapToolIdentify.__init__(self, window.mapCanvas)
        self.window = window

    def canvasReleaseEvent(self, event):
        found_features = self.identify(event.x(), event.y(),
                                       self.TopDownStopAtFirst,
                                       self.VectorLayer)
        if len(found_features) > 0:
            layer = found_features[0].mLayer
            feature = found_features[0].mFeature
            geometry = feature.geometry()

            info = []

            name = feature.attribute("NAME")
            if name != None: info.append(name)

            admin_0 = feature.attribute("ADM0NAME")
            admin_1 = feature.attribute("ADM1NAME")
            if admin_0 and admin_1:
                info.append(admin_1 + ", " + admin_0)

            timezone = feature.attribute("TIMEZONE")
            if timezone != None:
                info.append("Timezone: " + timezone)

            longitude = geometry.asPoint().x()
            latitude  = geometry.asPoint().y()
            info.append("Lat/Long: %0.4f, %0.4f" % (latitude, longitude))

            QMessageBox.information(self.window,
                                    "Feature Info",
                                    "\n".join(info))

#############################################################################

class PanTool(QgsMapTool):
    def __init__(self, mapCanvas):
        QgsMapTool.__init__(self, mapCanvas)
        self.setCursor(Qt.OpenHandCursor)
        self.dragging = False

    def canvasMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.canvas().panAction(event)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.canvas().panActionEnd(event.pos())
            self.dragging = False

#############################################################################

