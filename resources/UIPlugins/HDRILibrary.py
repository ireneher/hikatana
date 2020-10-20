# import os
#
# # Import PyQt5 or PyQt4 (depends on Katana version)
# try:
#     import PyQt5
#
# except ImportError:
#     print("PyQt5 not available")
#     try:
#         import PyQt4
#
#     except ImportError:
#         print("PyQt4 not available")
#         raise
#     else:
#         from Katana import QtCore, QtGui
#         BINDING = "PyQt4"
#         class QtModuleCompatibility(object):
#             def __getattr__(self, attr):
#                 return getattr(QtGui, attr)
#
#         QtWidgets = QtModuleCompatibility()
# else:
#     BINDING = "PyQt5"
#     from Katana import QtCore, QtGui, QtWidgetsfrom Katana import QT4FormWidgets, UI4, AssetAPI, logging

from Katana import QtCore, QtGui, QtWidgets
from UI4.Util import AssetWidgetDelegatePlugins


class KatanaBamsBrowser(QtWidgets.QFrame):
    """
    Provides BamsBrowser as a means of selecting filepaths for products
    """

    # if BINDING == "PyQt5":
    #     selectionValidSignal = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(KatanaBamsBrowser, self).__init__(parent=parent)

        # Valid selection needs to be stored in the event that the user toggles tabs
        self.__valid = False

        # # Populate the browser from the current context
        # ctx = Context.from_environment(validate=False)
        #
        # # ----- Widgets -----
        #
        # self.bams_browser = bams_ui.BamsBrowser.default(context=ctx)
        # self.bams_browser.output_browser.set_default_actions(
        #     output_browser.Actions.NoActions
        # )
        # self.bams_browser.output_browser.set_selection_mode(
        #     output_browser.Selection.Single
        # )
        #
        # # ----- Layout -----
        #
        # layout = QtWidgets.QVBoxLayout(self)
        # layout.addWidget(self.bams_browser)
        #
        # # ----- Connections -----
        #
        # self.bams_browser.entitiesSelected.connect(self._on_selection_changed)

    def getResult(self):
        """
        Required by Katana

        :rtype: str
        """
        pass
        # selected = self.bams_browser.output_browser.get_selected_entities()
        # return str(selected[0].filepath) if len(selected) == 1 else ""

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
        # try:
        #     # If no location is given, set it to the current environment location
        #     ctx = (
        #         Context.from_path(location, validate=False)
        #         if location
        #         else Context.from_environment()
        #     )
        #     self.bams_browser.set_context(ctx)
        # except ContextError:
        #     pass
        # except Exception as e:
        #     _logDebug("Failed to set location with unknown error: {}".format(e))

        pass

    def setSaveMode(self, saveMode):
        """
        Optional Katana method for modifying behaviour if saving

        :param bool saveMode:
        """
        # BamsBrowser cannot be used to save
        #self.bams_browser.setEnabled(not saveMode)
        pass

    def _on_selection_changed(self, output_entities):
        """
        :param list[bams_client.OutputEntity] output_entities:
        """
        # self.__valid = bool(output_entities)
        # if __binding__ in ("PySide2", "PyQt5"):
        #     self.selectionValidSignal.emit(self.__valid)
        # elif __binding__ in ("PySide", "PyQt4"):
        #     self.emit(QtCore.SIGNAL("selectionValid"), self.__valid)
        pass


class BamsBrowserAssetWidgetDelegate(
    AssetWidgetDelegatePlugins.DefaultAssetWidgetDelegate
):
    def configureAssetBrowser(self, browser):
        """
        Optional Katana method for configuring the tabs on the asset browser
        """
        super(BamsBrowserAssetWidgetDelegate, self).configureAssetBrowser(browser)
        value_policy = self.getValuePolicy()
        hints = value_policy.getWidgetHints()

        # Gets a browser for the current project
        index = browser.addBrowserTab(KatanaBamsBrowser, "HDRILibrary")
        # except ContextError:
        #     log.warn(
        #         "Skipping the registry of bams browser, loaded katana "
        #         "outside a production context"
        #     )
        #     return False
        #
        # # Set the shot to match the currently used filepath
        # input_path = str(value_policy.getValue())
        # browser.getBrowser(index).setLocation(input_path)
        #
        # # Set the filters to only show contextual files
        # filters = {"matches": {"is_published": True, "is_deleted": False}}
        # if hints.get("context") == AssetAPI.kAssetContextAlembic:
        #     filters["matches"]["representation"] = "abc"
        #
        # browser.getBrowser(index).bams_browser.output_browser.set_filters(filters)

    def shouldAddFileTabToAssetBrowser(self):
        """
        :rtype: bool
        """
        # Yes we want to keep the file tab in the asset browser
        return True


# Register the widget delegate to be associated with File Assets
PluginRegistry = [("AssetWidgetDelegate", 1, "File", BamsBrowserAssetWidgetDelegate)]