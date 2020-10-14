import PackageSuperToolAPI.NodeUtils as SuperToolUtils
from PyQt5 import QtWidgets, QtGui, QtCore
from Katana import (
    NodegraphAPI,
    Utils,
    UniqueName,
    FormMaster,
    UI4,
    QT4Widgets,
    QT4FormWidgets,
    Widgets,
)


import Constants
import ScriptActions


class Signals(QtCore.QObject):
    colourChangeSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(Signals, self).__init__(parent)

    def broadcastColourChange(self, colourCollectionItem):
        self.colourChangeSignal.emit(colourCollectionItem)


class ColourCollectionsList(QtWidgets.QListWidget):
    def __init__(self, root, parent=None):
        super(ColourCollectionsList, self).__init__(parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onRightClick)
        self.setIconSize(QtCore.QSize(60, 20))
        self.setSpacing(5)
        self.root = root
        self.signals = Signals()

    def onRightClick(self, pos):
        """
        Custom menu with options:
            - Change colour
            - Select in SceneGraph
        """
        menu = QtWidgets.QMenu()
        menu.move(QtGui.QCursor().pos())
        currentItem = self.itemAt(pos)
        if currentItem:
            colourAction = menu.addAction("Change Colour")
            selectAction = menu.addAction("Select in SceneGraph")

            colourAction.triggered.connect(lambda: self.changeColour(currentItem))
            selectAction.triggered.connect(lambda: self.selectInScenegraph(currentItem))

            menu.exec_()

    def changeColour(self, collectionItem):
        chosenColour = QtWidgets .QColorDialog.getColor()
        collectionItem.changeColour(chosenColour)
        self.signals.broadcastColourChange(collectionItem)

    def selectInScenegraph(self, collectionItem):
        # Importing here to avoid doing so in non-interactive mode
        from Katana import Widgets
        cel = "{}/${}".format(self.root, collectionItem.name)
        collector = Widgets.CollectAndSelectInScenegraph(cel, self.root)
        collector.collectAndSelect()


class ColourCollectionItem(QtWidgets.QListWidgetItem):
    def __init__(self, name, colour, parent=None):
        super(ColourCollectionItem, self).__init__(name, parent=parent)
        self.name = name
        self.colour = colour
        pixmap = QtGui.QPixmap(300, 100)
        pixmap.fill(QtGui.QColor.fromRgbF(self.colour[0], self.colour[1], self.colour[2], alpha=self.colour[3]))
        icon = QtGui.QIcon(pixmap)
        self.setIcon(icon)
        font = self.font()
        font.setPointSize(15)
        font.setBold(True)
        self.setFont(font)

    def changeColour(self, newQColor):
        self.colour = newQColor.getRgbF()
        pixmap = QtGui.QPixmap(300, 100)
        pixmap.fill(newQColor)
        icon = QtGui.QIcon(pixmap)
        self.setIcon(icon)


class ColourCollectionsEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        super(ColourCollectionsEditor, self).__init__(parent=parent)
        node.upgrade()
        self.node = node
        self.root = Constants.DEFAULT_LOCATION
        self.collections = {}
        self.items = []
        layout = QtWidgets.QVBoxLayout(self)

        # Root parameter
        self.locationPolicy = UI4.FormMaster.CreateParameterPolicy(
            None, self.node.getParameter(Constants.LOCATION_PARAM)
        )
        factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        self.locationWidget = factory.buildWidget(self, self.locationPolicy)
        self.locationPolicy.addCallback(self.__onLocationChanged)
        layout.addWidget(self.locationWidget)

        # This widget is not displayed, it is used for scenegraph callback purposes
        self.scenegraphViewRoot = UI4.Widgets.SceneGraphView()
        self.scenegraphViewRoot.addTopLevelLocation(self.root)
        self.scenegraphViewRoot.setLocationAddedOrUpdatedCallback(self._onLocationDataUpdated)

        self.collectionsList = ColourCollectionsList(self.root)
        self.collectionsList.signals.colourChangeSignal.connect(self.onColourChanged)
        layout.addWidget(self.collectionsList)

        # Button to refresh (re-cook and update)
        # Usually not needed, but available if necessary
        self.refreshButton = UI4.Widgets.ToolbarButton(
            "Refresh",
            self,
            UI4.Util.IconManager.GetPixmap("Icons/reload16.png"),
            rolloverPixmap=UI4.Util.IconManager.GetPixmap("Icons/reload_hilite16.png"),
        )
        self.refreshButton.clicked.connect(self.updateCollections)
        layout.addWidget(self.refreshButton)

    def _onLocationDataUpdated(self, *args):
        # Do not want to expand materials root location as it is changed
        # in updateCollections and only changes in the materialAssign attribute
        # of mesh locations are of interest
        if not args[0].startswith(Constants.DEFAULT_MAT_LOCATION):
            self.scenegraphViewRoot.setLocationExpandedRecursive(
                args[0], args[0]
            )
            if not self.scenegraphViewRoot.isProcessing():
                self.updateCollections()

    def __onLocationChanged(self, *args, **kwargs):
        self.root = self.locationPolicy.getValue()
        self.scenegraphViewRoot.addTopLevelLocation(self.root)
        self.updateCollections()

    def updateCollections(self, *args):
        # Cook at Dot node, aka at 'clean' point before any new attribute has been set by SuperTool
        collectionNames = ScriptActions.cookCollections(root=self.root,
                                                        node=SuperToolUtils.GetRefNode(self.node,
                                                                                       Constants.DOT_KEY
                                                                                       )
                                                        ).keys()
        ScriptActions.setColourAttributes(collectionNames,
                                          stack=SuperToolUtils.GetRefNode(self.node,
                                                                          Constants.ATTRSET_KEY
                                                                          ),
                                          root=self.root,
                                          )

        # Re-cook since previous nodes added attributes
        self.collections = ScriptActions.cookCollections(root=self.root,
                                                         node=SuperToolUtils.GetRefNode(self.node,
                                                                                        Constants.ATTRSET_KEY
                                                                                        )
                                                         )
        _, preAssignedMats = ScriptActions.buildMaterials(self.collections,
                                                            stack=SuperToolUtils.GetRefNode(self.node,
                                                                                         Constants.MAT_KEY
                                                                                         ),
                                                            node=SuperToolUtils.GetRefNode(self.node,
                                                                                        Constants.DOT_KEY
                                                                                        )
                                                            )

        ScriptActions.createAssignOpScripts(self.collections.keys(),
                                            stack=SuperToolUtils.GetRefNode(self.node,
                                                                            Constants.OPSCRIPT_ASSIGN_KEY
                                                                            ),
                                            root=self.root)

        ScriptActions.createOverrideOpScripts(preAssignedMats,
                                              stack=SuperToolUtils.GetRefNode(self.node,
                                                                              Constants.OPSCRIPT_OVERRIDE_KEY
                                                                              ),
                                              root=self.root)

        self.collectionsList.clear()
        self.items = []  # Need to store items so Qt doesn't remove the objects from memory after the clear call
        idx = 0
        for collection, attrs in self.collections.items():
            self.items.append(ColourCollectionItem(collection, attrs["colour"]))
            self.collectionsList.addItem(self.items[idx])
            idx = idx + 1

    def onColourChanged(self, item):
        ScriptActions.editColour(item.name, item.colour, self.node)

    def onCollectionParamChanged(self, events):
        for _, _, evData in events:
            node = evData["node"]
            param = evData["param"]
            if(
                    node.getType() == "CollectionCreate"
                    and param.getName() in ("name", "location")
            ) or (
                    node.getType == "MaterialAssign"
                    and param.getName() in ("materialAssign", "CEL")
            ):
                    self.updateCollections()

    def onCollectionNodeChanged(self, events):
        for _, _, evData in events:
            node = evData["node"]
            if node.getType() in ("CollectionCreate", "MaterialAssign"):
                self.updateCollections()

    def onConnectionChanged(self, events):
        for _, _, evData in events:
            if evData["portB"] == self.node.getInputPortByIndex(0):
                self.updateCollections()

