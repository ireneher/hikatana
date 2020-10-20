from PyQt5 import QtWidgets
from Katana import AssetBrowser


class HDRITab(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(HDRITab, self).__init__(parent=parent)

        self.__valid = False

        # ----- Widgets -----
        # QFileDialog with Icon provider

        # ----- Layout -----

        layout = QtWidgets.QVBoxLayout(self)

        # ----- Connections -----

    def getResult(self):
        """
        Required by Katana

        :rtype: str
        """
        pass
        # return filepath

    def selectionValid(self):
        """
        Required by Katana

        :rtype: bool
        """
        return self.__valid

    def setLocation(self, location):
        """
        Optional Katana method for setting the current path

        :param str  location:
        :return:
        """
        pass


class HDRIBrowser(AssetBrowser.Browser.BrowserDialog):
    def __init__(self, *args, **kargs):
        super(HDRIBrowser, self).__init__(*args, **kargs)
        self.addBrowserTab(HDRITab, "HDRI Library")


def launch(node, selectedItems):
    browser = HDRIBrowser()
    browser.exec_()