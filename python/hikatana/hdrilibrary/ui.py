import os

from PyQt5 import QtWidgets, QtCore, QtGui
from Katana import AssetBrowser, QT4Browser

IMAGE_TYPES = (".jpg", ".tiff", ".png", ".exr", ".psd", ".hdri", ".hdr")


class Signals(QtCore.QObject):
    fileSelected = QtCore.pyqtSignal(object)
    favouriteSelected = QtCore.pyqtSignal(object)

    def __init__(self):
        super(Signals, self).__init__()


class IconProvider(QtWidgets.QFileIconProvider):
    def __init__(self):
        super(IconProvider, self).__init__()

    def icon(self, icontypeOrQfileinfo):
        if isinstance(icontypeOrQfileinfo, QtWidgets.QFileIconProvider.IconType):
            return super(IconProvider, self).icon(icontypeOrQfileinfo)
        else:
            fileInfo = icontypeOrQfileinfo
            if fileInfo.filePath().endswith(IMAGE_TYPES):
                pixmap = QtGui.QPixmap()
                pixmap.load(fileInfo.absoluteFilePath())

                return QtGui.QIcon(pixmap)

            else:
                return super(IconProvider, self).icon(fileInfo)


class FavouritesWidget(QtWidgets.QListWidget):
    def __init__(self, signals, parent=None):
        super(FavouritesWidget, self).__init__(parent=parent)
        self.signals = signals
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setAcceptDrops(True)
        # TODO read from json
        self.favourites = []
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onRightClick)
        self.clicked.connect(self.onClicked)

    def onClicked(self):
        self.signals.favouriteSelected.emit(str(self.currentItem().text()))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(FavouritesWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            super(FavouritesWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            filePaths = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    filePaths.append(str(url.toLocalFile()))
            self.addItems(filePaths)
            self.favourites.extend(filePaths)
        else:
            super(FavouritesWidget, self).dropEvent(event)

    def onRightClick(self, pos):
        menu = QtWidgets.QMenu()
        currentCursor = QtGui.QCursor().pos()
        currentItem = self.itemAt(pos)
        menu.move(currentCursor)
        remove_action = menu.addAction("Remove favourite")
        remove_action.triggered.connect(
            lambda: self.removeFavourite(currentItem)
        )
        menu.exec_()

    def removeFavourite(self,  item):
        if str(item.text()) in self.favourites:
            self.favourites.remove(str(item.text()))
        self.takeItem(self.row(item))


class HDRITab(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(HDRITab, self).__init__(parent=parent)
        screenGeometry = QtWidgets.QDesktopWidget.screenGeometry(
            QtWidgets.QDesktopWidget()
        )
        self.setMinimumWidth(screenGeometry.width() * 0.5)
        self.setMinimumHeight(screenGeometry.height() * 0.5)

        self.signals = Signals()
        self.__valid = True

        # ----- Components -----
        # Splitter
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setWindowState(QtCore.Qt.WindowMaximized)
        # Favourites
        self.favouritesWidget = FavouritesWidget(self.signals, parent=self.splitter)
        # Directories model
        localKatanaDir = os.path.join(os.path.expanduser("~"), ".katana")
        self.dirModel = QtWidgets.QFileSystemModel()
        self.dirModel.setRootPath(localKatanaDir)
        self.dirModel.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)
        # Files model
        self.filesModel = QtWidgets.QFileSystemModel()
        self.filesModel.setRootPath(localKatanaDir)
        self.filesModel.setFilter(QtCore.QDir.Files)
        self.filesModel.setIconProvider(IconProvider())
        self.filesModel.setNameFilterDisables(False)
        self.filesModel.setNameFilters(["*{}".format(imageType) for imageType in IMAGE_TYPES])
        # Side tree view
        self.treeView = QtWidgets.QTreeView(self.splitter)
        self.treeView.setModel(self.dirModel)
        self.treeView.hideColumn(1)
        self.treeView.hideColumn(2)
        self.treeView.hideColumn(3)
        self.treeView.resizeColumnToContents(0)
        self.treeView.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.treeView.setDragEnabled(True)
        # Main image view
        self.thumbnailView = QtWidgets.QListView(self.splitter)
        self.thumbnailView.setModel(self.filesModel)
        self.thumbnailView.setIconSize(QtCore.QSize(210, 90))
        self.thumbnailView.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        # ----- Layout -----
        self.splitter.setStretchFactor(1, 4)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.splitter)

        # ----- Connections -----
        self.treeView.clicked.connect(self.onTreeClicked)
        self.signals.favouriteSelected.connect(self.onFavouriteSelected)

    def onFavouriteSelected(self, root):
        self.thumbnailView.setRootIndex(self.filesModel.setRootPath(root))

    def onSelectionChanged(self, index):
        self.signals.fileSelected.emit(self.filesModel.filePath(self.thumbnailView.currentIndex()))

    def onTreeClicked(self, index):
        self.thumbnailView.setRootIndex(self.filesModel.setRootPath(self.dirModel.filePath(index)))

    def selectionValid(self):
        return self.__valid


class HDRIBrowser(AssetBrowser.Browser.BrowserDialog):
    def __init__(self, *args, **kargs):
        super(HDRIBrowser, self).__init__(*args, **kargs)
        libraryID = self.addBrowserTab(HDRITab, "HDRI Library")
        self.libraryTab = self.getBrowser(libraryID)
        self.result = ""
        self.libraryTab.signals.fileSelected.connect(self.updateResult)

    def updateResult(self, filepath):
        self.result = filepath

    def getResult(self):
        # TODO write to json
        print(self.libraryTab.favouritesWidget.favourites)
        return self.result


def launch(node, selectedItems):
    browser = HDRIBrowser()
    if browser.exec_() == browser.Accepted:
        print browser.getResult()
