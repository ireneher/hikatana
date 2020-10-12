import PackageSuperToolAPI
import PackageSuperToolAPI.NodeUtils as SuperToolUtils
from PyQt5 import QtWidgets, QtGui
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


class ColourCollectionsEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        super(ColourCollectionsEditor, self).__init__(parent=parent)
        node.upgrade()
        self.node = node
        # TODO callback on new collection created (name param finalised) -> cook, set, assign
        self.collection_names = ScriptActions.cookCollections(node=self.node)
        ScriptActions.setColourAttributes(self.collection_names,
                                          stack=SuperToolUtils.GetRefNode(self.node,
                                                                          Constants.ATTRSET_KEY
                                                                          )
                                          )
        ScriptActions.assignMaterials(self.collection_names,
                                      stack=SuperToolUtils.GetRefNode(self.node,
                                                                      Constants.MATASSIGN_KEY
                                                                      )
                                      )

