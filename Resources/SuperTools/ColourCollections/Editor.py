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
        pixmap.fill(QtGui.QColor.fromRgbF(colour[0], colour[1], colour[2], alpha=colour[3]))
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
        self.collections = {}
        layout = QtWidgets.QVBoxLayout(self)
        Utils.EventModule.RegisterCollapsedHandler(
            self.__on_node_editedOrViewed, "node_setEdited"
        )
        Utils.EventModule.RegisterCollapsedHandler(
            self.__on_node_editedOrViewed, "node_setViewed"
        )

        # TODO: Option to Set Colours on node view (and label explaining)
        # TODO add location param for collections root
        self.registerCallbacks()
        self.collectionsList = ColourCollectionsList()
        layout.addWidget(self.collectionsList)
        self.updateCollections()

    def __on_node_editedOrViewed(self, args):
        if self.node in NodegraphAPI.GetAllEditedNodes() or self.node in NodegraphAPI.GetViewNodes():
            self.updateCollections()

    def registerCallbacks(self):
        Utils.EventModule.RegisterCollapsedHandler(self.onNewCollection,
                                                   eventType="parameter_finalizeValue")
        Utils.EventModule.RegisterCollapsedHandler(self.onRemovedCollection,
                                                   eventType="node_setBypassed")
        Utils.EventModule.RegisterCollapsedHandler(self.onRemovedCollection,
                                                   eventType="node_delete")

    def updateCollections(self, *args):
        # Cook at Dot node, aka at 'clean' point before any new attribute has been set by SuperTool
        collectionNames = ScriptActions.cookCollections(node=SuperToolUtils.GetRefNode(self.node,
                                                                                       Constants.DOT_KEY
                                                                                       )).keys()
        print(collectionNames)
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
                                                                                        Constants.MATASSIGN_KEY
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

    def onRemovedCollection(self, events):
        for _, _, evData in events:
            node = evData["node"]
            if node.getType() == "CollectionCreate":
                self.updateCollections()


