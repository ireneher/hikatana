import os
import json

from PyQt5 import QtWidgets, QtCore, QtGui
from Katana import AssetBrowser, QT4Browser, OpenEXR, Imath

from hikatana.hdrilibrary import constants

class Exr(object):
    def __init__(self):
        super(exr, self).__init__()

    @classmethod
    def getEXR(exrPath):
        width = 280
        height = 160

        imageq = PilImageQt(exrToJpg(exrPath))
        qimage = QtGui.QImage(imageq)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        ScaledPixmap = pixmap.scaled(width, height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)

        return ScaledPixmap

    @classmethod
    def exrToJpg(exrfile):
        file = OpenEXR.InputFile(exrfile)
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        dw = file.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        img = QtGui.QImage(size[0], size[1], QtGui.QImage.Format_RGB16);
        for y in range (0, img.height()):
            memcpy(img->scanLine(y), rawData[y], img->bytesPerLine());
        rgbf = [Image.fromstring("F", size, file.channel(c, pt)) for c in "RGB"]

        extrema = [im.getextrema() for im in rgbf]
        darkest = min([lo for (lo,hi) in extrema])
        lighest = max([hi for (lo,hi) in extrema])
        scale = 255 / (lighest - darkest)
        def normalize_0_255(v):
            return (v * scale) + darkest
        rgb8 = [im.point(normalize_0_255).convert("L") for im in rgbf]
        myjpg = Image.merge("RGB", rgb8)
        return myjpg

class Preferences(object):
    def __init__(self, location=None, name=None):
        super(Preferences, self).__init__()
        self.location = location or os.path.join(os.path.expanduser("~"), ".katana")
        self.name = "{}.txt".format(name) if name else "HIPrefs.txt"
        self.path = os.path.join(self.location, self.name)

    def build(self, dataList, componentKey, toolKey=constants.TOOL_PREFS_KEY):
        return {toolKey: {
            componentKey: dataList
            }
        }

    def write(self, data):
        if not os.path.exists(self.location):
            os.makedirs(self.location)

        if os.path.exists(self.path):
            os.remove(self.path)

        with open(self.path, 'w') as outfile:
            json.dump(data, outfile)

    def read(self):
        if not os.path.exists(self.path):
            return []

        with open(self.path) as infile:
            data = json.load(infile)

        return data


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
            if fileInfo.filePath().endswith(constants.UNSUPPORTED_IMAGE_TYPES):
                pixmap = Exr.getEXR(fileInfo.filePath())
                return QtGui.QIcon(pixmap)

            elif fileInfo.filePath().endswith(constants.IMAGE_TYPES):
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

        prefs = Preferences().read()
        self.favourites = prefs[constants.TOOL_PREFS_KEY][constants.FAVOURITES_PREFS_KEY] if prefs else []
        self.addItems(self.favourites)
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
        self.filesModel.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        self.filesModel.setIconProvider(IconProvider())
        self.filesModel.setNameFilterDisables(False)
        self.nameFilters = ["*{}".format(imageType) for imageType in constants.IMAGE_TYPES]
        self.extendedNameFilters = []  # to be populated by search bar
        self.filesModel.setNameFilters(self.nameFilters)
        # Side tree view
        self.treeView = QtWidgets.QTreeView(self.splitter)
        self.treeView.setModel(self.dirModel)
        self.treeView.hideColumn(1)
        self.treeView.hideColumn(2)
        self.treeView.hideColumn(3)
        self.treeView.resizeColumnToContents(0)
        self.treeView.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.treeView.setDragEnabled(True)
        self.treeView.expandAll()
        # Main image view
        self.thumbnailView = QtWidgets.QListView(self.splitter)
        self.thumbnailView.setModel(self.filesModel)
        self.thumbnailView.setIconSize(QtCore.QSize(210, 90))
        self.thumbnailView.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        # Search bar
        self.searchBar = QtWidgets.QLineEdit()
        self.searchBar.setPlaceholderText("Search")
        self.searchBar.setFont(QtGui.QFont("Open Sans", 12))

        # ----- Layout -----
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setStretchFactor(2, 4)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.searchBar)
        layout.addWidget(self.splitter)

        # ----- Connections -----
        self.treeView.clicked.connect(self.onTreeClicked)
        self.signals.favouriteSelected.connect(self.onFavouriteSelected)
        self.searchBar.textChanged.connect(self.search)

    def search(self, searchStr):
        if searchStr:
            searchStr = "*{}".format(searchStr)
            self.extendedNameFilters = [searchStr+f for f in self.nameFilters]
            self.filesModel.setNameFilters(self.extendedNameFilters)
        else:
            self.extendedNameFilters = []
            self.filesModel.setNameFilters(self.nameFilters)

    def onFavouriteSelected(self, root):
        self.thumbnailView.setRootIndex(self.filesModel.setRootPath(root))
        self.filesModel.setNameFilters(self.extendedNameFilters or self.nameFilters)

    def onSelectionChanged(self, index):
        self.signals.fileSelected.emit(self.filesModel.filePath(self.thumbnailView.currentIndex()))

    def onTreeClicked(self, index):
        self.thumbnailView.setRootIndex(self.filesModel.setRootPath(self.dirModel.filePath(index)))
        self.filesModel.setNameFilters(self.extendedNameFilters or self.nameFilters)

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
        prefs = Preferences()
        data = prefs.build(self.libraryTab.favouritesWidget.favourites, constants.FAVOURITES_PREFS_KEY)
        Preferences().write(data)
        return self.result


def launch(node, selectedItems):
    browser = HDRIBrowser()
    if browser.exec_() == browser.Accepted:
        print browser.getResult()
