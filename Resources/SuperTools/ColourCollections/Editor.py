import PackageSuperToolAPI
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


class ColourCollectionsList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(ColourCollectionsList, self).__init__(parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested[QtCore.QPoint].connect(self.onRightClick)
        self.setIconSize(QtCore.QSize(60, 20))
        self.setSpacing(5)

    def onRightClick(self):
        """
        Custom menu with options:
            - Change colour
            - Select in SceneGraph
        """
        menu = QtWidgets.QMenu()
        currentCursor = QtGui.QCursor().pos()
        menu.move(currentCursor)
        currentItem = self.itemAt(currentCursor)
        colourAction = menu.addAction("Change Colour")
        selectAction = menu.addAction("Select in SceneGraph")

        colourAction.triggered.connect(lambda: self.changeColour(currentItem))
        selectAction.triggered.connect(lambda: self.selectInScenegraph(currentItem))

        menu.exec_()

    def changeColour(self, collectionItem):
        pass

    def selectInScenegraph(self, collectionItem):
        pass


class ColourCollectionItem(QtWidgets.QListWidgetItem):
    def __init__(self, name, colour, parent=None):
        super(ColourCollectionItem, self).__init__(name, parent=parent)
        pixmap = QtGui.QPixmap(300, 100)
        pixmap.fill(QtGui.QColor(colour[0]*255, colour[1]*255, colour[2]*255, alpha=colour[3]*255))
        icon = QtGui.QIcon(pixmap)
        self.setIcon(icon)
        font = self.font()
        font.setPointSize(15)
        font.setBold(True)
        self.setFont(font)


class ColourCollectionsEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        super(ColourCollectionsEditor, self).__init__(parent=parent)
        node.upgrade()
        self.node = node
        layout = QtWidgets.QVBoxLayout(self)
        self.scenegraphView = UI4.Widgets.SceneGraphView()
        self.scenegraphView.addTopLevelLocation("/root")
        self.scenegraphView.setLocationDataProcessedCallback(self.updateCollections)
        self.collections = {}
        Utils.EventModule.RegisterCollapsedHandler(self.onNewCollection,
                                                   eventType="parameter_finalizeValue")

        # TODO: Option to Set Colours on node view (and label explaining)
        # self.__remove_button = UI4.Widgets.ToolbarButton(
        #     "Delete lightgroup",
        #     self,
        #     UI4.Util.IconManager.GetPixmap("Icons/multiply16.png"),
        #     rolloverPixmap=UI4.Util.IconManager.GetPixmap("Icons/multiplyHilite16.png"),
        # )
        # TODO add location param for collections root

        self.collectionsList = ColourCollectionsList()
        layout.addWidget(self.collectionsList)

    def updateCollections(self, *args):
        collectionNames = ScriptActions.cookCollections(node=self.node).keys()
        ScriptActions.setColourAttributes(collectionNames,
                                          stack=SuperToolUtils.GetRefNode(self.node,
                                                                          Constants.ATTRSET_KEY
                                                                          )
                                          )
        ScriptActions.assignMaterials(collectionNames,
                                      stack=SuperToolUtils.GetRefNode(self.node,
                                                                      Constants.MATASSIGN_KEY
                                                                      )
                                      )
        # Re-cook since previous nodes added attributes
        self.collections = ScriptActions.cookCollections(node=SuperToolUtils.GetRefNode(self.node,
                                                                                        Constants.OPSCRIPT_KEY
                                                                                        )
                                                         )
        self.collectionsList.clear()
        self.items = []
        idx=0
        for collection, attrs in self.collections.items():
            self.items.append(ColourCollectionItem(collection, attrs["colour"]))
            self.collectionsList.addItem(self.items[idx])
            idx = idx + 1

    def onNewCollection(self, events):
        for _, _, evData in events:
            node = evData["node"]
            param = evData["param"]
            if (
                    node.getType() == "CollectionCreate"
                    and param.getName() == "name"
            ):
                self.updateCollections()


