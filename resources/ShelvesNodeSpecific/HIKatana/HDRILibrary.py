"""
NAME: HDRI Library
ICON: icon.png
DROP_TYPES:
SCOPE: GafferThree

Open HDRI browser to populate image in currently selected light(s).

"""

from hikatana.hdrilibrary import ui as HDRILibraryUI

HDRILibraryUI.launch(globals()["node"], globals()["selectedItems"])
