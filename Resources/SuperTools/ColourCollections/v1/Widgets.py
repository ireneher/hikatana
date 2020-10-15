from PyQt5 import QtWidgets, QtGui, QtCore


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
        if chosenColour.isValid():
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
