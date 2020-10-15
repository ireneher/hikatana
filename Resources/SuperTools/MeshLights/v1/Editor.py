import PackageSuperToolAPI.NodeUtils as SuperToolUtils
from PyQt5 import QtWidgets, QtGui
from Katana import (
    UI4,
)

import Constants
import ScriptActions


class MeshLightsEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        super(MeshLightsEditor, self).__init__(parent=parent)
        node.upgrade()
        self.node = node
        layout = QtWidgets.QVBoxLayout(self)
        factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory

        # CEL
        self.celParamPolicy = UI4.FormMaster.CreateParameterPolicy(
            None, self.node.getParameter(Constants.CEL_PARAM)
        )
        self.celWidget = factory.buildWidget(self, self.celParamPolicy)
        layout.addWidget(self.celWidget)

        # Gaffer teleparameter
        self.gafferParamPolicy = UI4.FormMaster.CreateParameterPolicy(
            None, self.node.getParameter(Constants.GAFFER_PARAM)
        )
        self.gafferWidget = factory.buildWidget(self, self.gafferParamPolicy)
        layout.addWidget(self.gafferWidget)

        self.labelWidget = UI4.Widgets.IconLabelFrame(
            UI4.Util.IconManager.GetPixmap("Icons/nodeCommentActive16.png"),
            'The name parameters are optional.<br>'
            '<b>Light name</b> defaults to the mesh SceneGraph location name followed by <i>Light</i>'
            'and an instance number.<br>'
            '<b>Rig name</b> defaults to <i>meshLightsRig</i>.', margin=8, parent=self
        )

        layout.addWidget(self.labelWidget)

        # Light name
        self.lightNameParamPolicy = UI4.FormMaster.CreateParameterPolicy(
            None, self.node.getParameter(Constants.LIGHT_NAME_PARAM)
        )
        self.lightNameWidget = factory.buildWidget(self, self.lightNameParamPolicy)
        layout.addWidget(self.lightNameWidget)

        # Rig name
        self.rigNameParamPolicy = UI4.FormMaster.CreateParameterPolicy(
            None, self.node.getParameter(Constants.RIG_NAME_PARAM)
        )
        self.rigNameParamWidget = factory.buildWidget(self, self.rigNameParamPolicy)
        layout.addWidget(self.rigNameParamWidget)

        # Option to append or override
        self.modeNameParamPolicy = UI4.FormMaster.CreateParameterPolicy(
            None, self.node.getParameter(Constants.MODE_PARAM)
        )
        self.modeParamWidget = factory.buildWidget(self, self.modeNameParamPolicy)
        layout.addWidget(self.modeParamWidget)

        # Button to populate the gaffer
        self.createButton = QtWidgets.QPushButton("Create Lights")
        self.createButton.clicked.connect(self.createLights)
        layout.addWidget(self.createButton)

    def createLights(self):
        ScriptActions.createMeshLights(
            SuperToolUtils.GetRefNode(self.node, Constants.GAFFER_NODE_KEY),
            self.celParamPolicy.getValue(),
            lightName=self.lightNameParamPolicy.getValue(),
            rigName=self.rigNameParamPolicy.getValue(),
            mode=self.modeNameParamPolicy.getValue()
        )