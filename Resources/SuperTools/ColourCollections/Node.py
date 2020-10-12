import PackageSuperToolAPI.NodeUtils as SuperToolUtils
import DrawingModule.AutoPosition as AutoPos
from Katana import NodegraphAPI, Utils, UniqueName

import Constants
import ScriptActions
import Upgrade


class ColourCollectionsNode(NodegraphAPI.SuperTool):
    def __init__(self):
        self.hideNodegraphGroupControls()
        self.addInputPort("in")
        self.addOutputPort("out")
        self.getParameters().createChildNumber("version", Constants.CURRENT_VERSION)
        self.__buildDefaultNetwork()
        if not self.getParent():
            self.setParent(NodegraphAPI.GetRootNode())

    def __buildDefaultNetwork(self):
        """
                                      |------------------------->|
        AttributeSetStack -> OpScript |--> MaterialAssignStack-->|Switch
        """
        # Create nodes and set parameters:

        attrSetStack = NodegraphAPI.CreateNode("GroupStack", self)
        attrSetStack.setChildNodeType("AttributeSet")

        opscriptNode = NodegraphAPI.CreateNode("OpScript", self)
        opscriptNode.getParameter("CEL").setValue("/root", 0.0)
        opscriptNode.getParameter("script.lua").setValue(Constants.OPSCRIPT, 0.0)

        materialAssignStack = NodegraphAPI.CreateNode("GroupStack", self)
        materialAssignStack.setChildNodeType("MaterialStack")

        switchNode = NodegraphAPI.CreateNode("Switch", self)
        switchNode.getParameter("in").setExpression("isNodeViewed(getParent().getNodeName())")

        # Make connections:
        self.getSendPort(self.getInputPortByIndex(0).getName()).connect(
            attrSetStack.getInputPortByIndex(0)
        )
        # Branch A
        attrSetStack.getOutputPortByIndex(0).connect(opscriptNode.getInputPortByIndex(0))
        opscriptNode.getOutputPortByIndex(0).connect(switchNode.addInputPort("i0"))

        # Branch B
        opscriptNode.getOutputPortByIndex(0).connect(materialAssignStack.getInputPortByIndex(0))
        materialAssignStack.getOutputPortByIndex(0).connect(switchNode.addInputPort("i1"))

        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            switchNode.getOutputPortByIndex(0)
        )

        AutoPos.AutoPositionNodes([attrSetStack, opscriptNode, materialAssignStack, switchNode])

        # Store references to nodes:
        SuperToolUtils.AddNodeRef(self, Constants.ATTRSET_KEY, attrSetStack)
        SuperToolUtils.AddNodeRef(self, Constants.OPSCRIPT_KEY, opscriptNode)
        SuperToolUtils.AddNodeRef(self, Constants.MATASSIGN_KEY, materialAssignStack)
        SuperToolUtils.AddNodeRef(self, Constants.SWITCH_KEY, switchNode)

    def upgrade(self):
        Upgrade.upgrade(self)

