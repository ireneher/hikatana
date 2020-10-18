import PackageSuperToolAPI.NodeUtils as SuperToolUtils
from Katana import NodegraphAPI

import Constants
import Upgrade


class MeshLightsNode(NodegraphAPI.SuperTool):
    def __init__(self):
        self.hideNodegraphGroupControls()
        self.addInputPort("in")
        self.addOutputPort("out")
        self.getParameters().createChildNumber(
            Constants.VERSION_PARAM, Constants.CURRENT_VERSION
        )
        gafferParam = self.getParameters().createChildString(
            Constants.GAFFER_PARAM, ""
        )

        celParam = self.getParameters().createChildString(Constants.CEL_PARAM, "")
        celParam.setHintString(repr({"widget": "cel"}))

        lightNameParam = self.getParameters().createChildString(Constants.LIGHT_NAME_PARAM, "")
        lightNameParam.setHintString(repr({"label": "Light name"}))

        rigNameParam = self.getParameters().createChildString(Constants.RIG_NAME_PARAM, "")
        rigNameParam.setHintString(repr({"label": "Rig name  "}))

        modeParam = self.getParameters().createChildString(Constants.MODE_PARAM, Constants.DEFAULT_MODE)
        modeParam.setHintString(repr({"widget": "popup",
                                      "options": Constants.MODE_OPTIONS,
                                      "label": "Mode    ",
                                      "help": "Append creates the new lights without clearing"
                                              "the Gaffer. <br>Override removes the current"
                                              "lights before adding the new ones."}))

        self.__buildDefaultNetwork()
        gafferNode = SuperToolUtils.GetRefNode(self, Constants.GAFFER_NODE_KEY)
        gafferParam.setExpression(
            "getNode('{}').getNodeName()".format(gafferNode.getName())
        )
        gafferParam.setHintString(repr({"widget": "teleparam"}))
        if not self.getParent():
            self.setParent(NodegraphAPI.GetRootNode())

    def __buildDefaultNetwork(self):
        """
        --> GafferThree-->
        """
        gafferNode = NodegraphAPI.CreateNode("GafferThree", self)
        SuperToolUtils.AddNodeRef(self, Constants.GAFFER_NODE_KEY, gafferNode)

        self.getSendPort("in").connect(gafferNode.getInputPortByIndex(0))
        gafferNode.getOutputPortByIndex(0).connect(self.getReturnPort("out"))

        # Set Gaffer to be expanded by default. Relevant for TeleParameter.
        gafferNode.getParameters().setHintString(repr({"open": True}))

        return [gafferNode]

    def upgrade(self):
        Upgrade.upgrade(self)
