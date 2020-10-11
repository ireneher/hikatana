import PackageSuperToolAPI
import PackageSuperToolAPI.NodeUtils as SuperToolUtils
from PyQt5 import QtWidgets
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


class ColourCollectionsEditor(PackageSuperToolAPI.BaseEditor.BaseEditor):
    def __init__(self, parent, node):
        super(ColourCollectionsEditor, self).__init__(parent, node)
        node.upgrade()
        self.node = node

        collectionsAttr = self.getAttribute("root/", "collections")
        print(collectionsAttr)
        print("~*"*50)