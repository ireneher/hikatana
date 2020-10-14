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
        location = self.getParameters().createChildString(
                        Constants.LOCATION_PARAM, Constants.DEFAULT_LOCATION
                    )
        location.setHintString(repr({"help": "SceneGraph location of collections",
                                     "widget": "newScenegraphLocation"}))

        self.__buildDefaultNetwork()
        if not self.getParent():
            self.setParent(NodegraphAPI.GetRootNode())

    def __buildDefaultNetwork(self):
        """
        MaterialStack -------------------------------->|
        Dot --> AttributeSetStack -> OpScriptStack |--> Merge
        """
        # Create nodes and set parameters:
        dotNode = NodegraphAPI.CreateNode("Dot", self)

        attrSetStack = NodegraphAPI.CreateNode("GroupStack", self)
        attrSetStack.setChildNodeType("AttributeSet")

        matCreateStack = NodegraphAPI.CreateNode("GroupStack", self)
        matCreateStack.setChildNodeType("Material")

        opscriptStack = NodegraphAPI.CreateNode("GroupStack", self)
        opscriptStack.setChildNodeType("OpScript")

        mergeNode = NodegraphAPI.CreateNode("Merge", self)
        mergeNode.getParameter('showAdvancedOptions').setValue("Yes", 0.0)
        mergeNode.getParameter('advanced.mergeGroupAttributes').insertArrayElement(0)
        mergeNode.getParameter('advanced.mergeGroupAttributes').getChildByIndex(0).setValue("material", 0.0)

        # Make connections:
        self.getSendPort(self.getInputPortByIndex(0).getName()).connect(
            dotNode.getInputPortByIndex(0)
        )

        # Branch A
        dotNode.getOutputPortByIndex(0).connect(attrSetStack.getInputPortByIndex(0))
        attrSetStack.getOutputPortByIndex(0).connect(opscriptStack.getInputPortByIndex(0))
        opscriptStack.getOutputPortByIndex(0).connect(mergeNode.addInputPort("i0"))

        # Branch B
        matCreateStack.getOutputPortByIndex(0).connect(mergeNode.addInputPort("i1"))

        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            mergeNode.getOutputPortByIndex(0)
        )

        AutoPos.AutoPositionNodes([dotNode, attrSetStack, matCreateStack, opscriptStack, mergeNode])

        # Store references to nodes:
        SuperToolUtils.AddNodeRef(self, Constants.DOT_KEY, dotNode)
        SuperToolUtils.AddNodeRef(self, Constants.ATTRSET_KEY, attrSetStack)
        SuperToolUtils.AddNodeRef(self, Constants.MAT_KEY, matCreateStack)
        SuperToolUtils.AddNodeRef(self, Constants.OPSCRIPT_KEY, opscriptStack)
        SuperToolUtils.AddNodeRef(self, Constants.MERGE_NODE_KEY, mergeNode)

    def upgrade(self):
        Upgrade.upgrade(self)
