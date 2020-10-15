import PackageSuperToolAPI.NodeUtils as SuperToolUtils
from PyQt5 import QtWidgets, QtGui, QtCore
from Katana import (
    UI4,
)


import Constants
import ScriptActions
import Widgets


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

        self.collectionsList = Widgets.ColourCollectionsList(self.root)
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
                                          SuperToolUtils.GetRefNode(self.node,
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
                                                          SuperToolUtils.GetRefNode(self.node,
                                                                                    Constants.MAT_KEY
                                                                                    ),
                                                          node=SuperToolUtils.GetRefNode(self.node,
                                                                                         Constants.DOT_KEY
                                                                                         )
                                                          )

        ScriptActions.createAssignOpScripts(self.collections.keys(),
                                            SuperToolUtils.GetRefNode(self.node,
                                                                      Constants.OPSCRIPT_ASSIGN_KEY
                                                                      ),
                                            root=self.root)

        ScriptActions.createOverrideOpScripts(preAssignedMats,
                                              SuperToolUtils.GetRefNode(self.node,
                                                                        Constants.OPSCRIPT_OVERRIDE_KEY
                                                                        ),
                                              root=self.root)

        self.collectionsList.clear()
        self.items = []  # Need to store items so Qt doesn't remove the objects from memory after the clear call
        idx = 0
        for collection, attrs in self.collections.items():
            self.items.append(Widgets.ColourCollectionItem(collection, attrs["colour"]))
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

