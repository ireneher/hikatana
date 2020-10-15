import random

import PackageSuperToolAPI.NodeUtils as SuperToolUtils
from Katana import FnGeolib, Nodes3DAPI, NodegraphAPI, FnAttribute, GeoAPI

from HIKatana import Utils
import Constants


def getCollectionCEL(collection, root="/root"):
    return "{}/${}".format(root, collection)


def getInverseCollectionCEL(collection, root="/root", material=None):
    if material:
        return r'( /root/world//* ){ attr("type") == "polymesh" or attr("type") == "subdmesh" and attr("materialAssign") == "'+ (
            material
        )+'" } - ' + (
            getCollectionCEL(collection, root)
        )
    return '( /root/world//* ){ attr("type") == "polymesh" or attr("type") == "subdmesh"} - ' + (
        getCollectionCEL(collection, root)
    )


def cookCollections(root="/root", node=None):
    client = Utils.getClient(node=node)
    cookedLoc = client.cookLocation(root)
    collectionsAttr = cookedLoc.getAttrs().getChildByName("collections")
    cookedCols = {}
    if collectionsAttr:
        for (colName, colAttr) in collectionsAttr.childList():
            attrDict = {}
            for (attrName, attr) in colAttr.childList():
                if isinstance(attr, FnAttribute.GroupAttribute):
                    for (subattrName, subAttr) in attr.childList():
                        attrDict[subattrName] = subAttr.getNearestSample(0.0)
                else:
                    attrDict[attrName] = attr.getNearestSample(0.0)
            # Ensure it is an actual collection and not a leftover attribute
            if "cel" in attrDict.keys():
                cookedCols.setdefault(colName, {}).update(attrDict)

    return cookedCols


def randomComponent():
    return round(random.random(), 4)


def doesCollectionExistInStack(collection, stack, userGroup=False):
    paramName = "collection" if not userGroup else "user.collection"
    for existingChildNode in stack.getChildNodes():
        if existingChildNode.getParameter(paramName).getValue(0.0) == collection:
            return existingChildNode

    return False


def clearStack(stack):
    for child in stack.getChildNodes():
        stack.deleteChildNode(child)


def cleanUpStack(collections, stack, userGroup=False):
    # Delete nodes referencing no-longer-existing collections
    for child in stack.getChildNodes():
        paramName = "collection" if not userGroup else "user.collection"
        if child.getParameter(paramName).getValue(0.0) not in collections:
            stack.deleteChildNode(child)


def setColourAttribute(collection, root="/root"):
    asNode = NodegraphAPI.CreateNode("AttributeSet", NodegraphAPI.GetRootNode())
    asNode.getParameter("celSelection").setValue(root, 0.0)
    asNode.getParameter("mode").setValue("CEL", 0.0)
    asNode.getParameter("attributeName").setValue("collections.{}.viewer".format(collection), 0.0)
    asNode.getParameter("attributeType").setValue("group", 0.0)
    asNode.getParameter("groupValue").createChildNumberArray("colour", 4)
    asNode.getParameter("groupValue.colour.i0").setValue(randomComponent(), 0.0)
    asNode.getParameter("groupValue.colour.i1").setValue(randomComponent(), 0.0)
    asNode.getParameter("groupValue.colour.i2").setValue(randomComponent(), 0.0)
    asNode.getParameter("groupValue.colour.i3").setValue(1.0, 0.0)
    asNode.getParameter("groupValue.colour").setHintString(repr({'widget': 'color'}))
    asNode.getParameters().createChildString("collection", collection)

    return asNode


def setColourAttributes(collections, stack, root="/root"):
    attrSetNodes = []
    if not stack:
        return
    cleanUpStack(collections, stack)
    for collection in collections:
        attrSetNode = setColourAttribute(collection, root=root)
        attrSetNodes.append(attrSetNode)
        if not doesCollectionExistInStack(collection, stack):
            stack.buildChildNode(attrSetNode)

    return attrSetNodes


def buildMaterialNode(name, namespace, colour, collection, stack):
    node = NodegraphAPI.CreateNode("Material", NodegraphAPI.GetRootNode())
    node.getParameter("name").setValue(name, 0.0)
    node.getParameter("namespace").setValue(namespace, 0.0)
    node.getParameters().createChildString("collection", collection)
    node.addShaderType("hydraSurface")
    node.getParameter("shaders.hydraSurfaceShader.enable").setValue(1.0, 0.0)
    node.getParameter("shaders.hydraSurfaceShader.value").setValue("katana_constant", 0.0)
    node.checkDynamicParameters()
    node.getParameter("shaders.hydraSurfaceParams.katanaColor.enable").setValue(1.0, 0.0)
    for idx, component in enumerate(colour):
        node.getParameter("shaders.hydraSurfaceParams.katanaColor.value.i{}".format(idx)).setValue(component, 0.0)

    stack.buildChildNode(node)

    return node


def buildMaterials(collections, stack):
    nodes = []
    if not stack:
        return
    for child in stack.getChildNodes():
        stack.deleteChildNode(child)

    for collection, attrs in collections.items():
        if "colour" not in attrs.keys():
            continue
        name = Constants.COLMATERIAL.format(collection)
        namespace = ""
        node = buildMaterialNode(name, namespace, attrs["colour"], collection, stack)
        nodes.append(node)

    return nodes


def createOpScript(collection, opscript, cel, root="/root"):
    node = NodegraphAPI.CreateNode("OpScript", NodegraphAPI.GetRootNode())
    node.getParameter("CEL").setValue(cel, 0.0)
    node.getParameter("script.lua").setValue(opscript, 0.0)
    node.getParameters().createChildGroup("user")
    node.getParameter("user").createChildString("collection", collection)
    node.getParameter("user").createChildString("root", root)
    return node


def createOpScripts(opscript, collections, stack, root="/root"):
    if not stack:
        return
    nodes = []
    cleanUpStack(collections, stack, userGroup=True)
    for collection in collections:
        colCEL = getCollectionCEL(collection, root=root)
        node = createOpScript(collection, opscript, colCEL)
        nodes.append(node)
        if not doesCollectionExistInStack(collection, stack, userGroup=True):
            stack.buildChildNode(node)

    return nodes


def createAssignOpScripts(collections, stack, root="/root"):
    createOpScripts(Constants.ASSIGN_OPSCRIPT, collections, stack, root=root)


def createOverrideOpScripts(collections, stack, root="/root"):
    createOpScripts(Constants.OVERRIDE_OPSCRIPT, collections, stack, root=root)


def editColour(collection, colour, parentNode):
    asStack = SuperToolUtils.GetRefNode(parentNode, Constants.ATTRSET_KEY)
    asNode = doesCollectionExistInStack(collection, asStack)
    for idx, component in enumerate(colour):
        asNode.getParameter("groupValue.colour.i{}".format(idx)).setValue(component, 0.0)

    mcStack = SuperToolUtils.GetRefNode(parentNode, Constants.MAT_KEY)
    mcNode = doesCollectionExistInStack(collection, mcStack)
    for idx, component in enumerate(colour):
        mcNode.getParameter("shaders.hydraSurfaceParams.katanaColor.value.i{}".format(idx)).setValue(component, 0.0)



