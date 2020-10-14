import random

import PackageSuperToolAPI.NodeUtils as SuperToolUtils
from Katana import FnGeolib, Nodes3DAPI, NodegraphAPI, FnAttribute, GeoAPI

import Constants


def getClient(node=None):
    Nodes3DAPI.CommitChanges()
    runtime = FnGeolib.GetRegisteredRuntimeInstance()
    transaction = runtime.createTransaction()
    client = transaction.createClient()
    if node:
        terminalOp = Nodes3DAPI.GetOp(transaction, node)
        transaction.setClientOp(client, terminalOp)
        runtime.commit(transaction)
    return client


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
    client = getClient(node=node)
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


def setColourAttributes(collections, stack=None, root="/root"):
    attrSetNodes = []
    if stack:
        cleanUpStack(collections, stack)
    for collection in collections:
        attrSetNode = setColourAttribute(collection, root=root)
        attrSetNodes.append(attrSetNode)
        if stack and not doesCollectionExistInStack(collection, stack):
            stack.buildChildNode(attrSetNode)

    return attrSetNodes


def buildMaterialNode(name, namespace, colour, collection, stack=None):
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

    if stack:
        stack.buildChildNode(node)

    return node


def buildMaterials(collections, stack=None, node=None, root="/root"):
    nodes = []
    for child in stack.getChildNodes():
        stack.deleteChildNode(child)

    preAssignedMats = {}
    client = getClient(node=node)
    for collection, attrs in collections.items():
        if "colour" not in attrs.keys():
            continue
        # If object already has a material assigned, create a viewer material at the same
        # location in order to later merge de attributes and not override it
        collectionPaths = GeoAPI.Util.CollectPathsFromCELStatement(client, attrs["cel"])
        for path in collectionPaths:
            cookedPath = client.cookLocation(path)
            if cookedPath.getAttrs() and cookedPath.getAttrs().getChildByName("materialAssign"):
                matAssign = cookedPath.getAttrs().getChildByName("materialAssign").getData()[0]
                if matAssign:
                    preAssignedMats.setdefault(collection, []).append(matAssign)
                    matAssign = matAssign.split("/root/materials/")[-1]  # Remove root to get namespace/name
                    name = matAssign.split("/")[-1]
                    namespace = matAssign.split(name)[0]
                    node = buildMaterialNode(name, namespace, attrs["colour"], collection, stack=stack)
                    nodes.append(node)

        # Always "custom" viewer material, for collections
        # whose members are a mix of shader-less and shaded
        name = Constants.COLMATERIAL.format(collection)
        namespace = ""
        node = buildMaterialNode(name, namespace, attrs["colour"], collection, stack=stack)
        nodes.append(node)

    return nodes, preAssignedMats


def createOpScript(collection, opscript, cel):
    node = NodegraphAPI.CreateNode("OpScript", NodegraphAPI.GetRootNode())
    node.getParameter("CEL").setValue(cel, 0.0)
    node.getParameter("script.lua").setValue(opscript, 0.0)
    node.getParameters().createChildGroup("user")
    node.getParameter("user").createChildString("collection", collection)
    return node


def createAssignOpScripts(collections, stack=None, root="/root"):
    nodes = []
    cleanUpStack(collections, stack, userGroup=True)
    for collection in collections:
        colCEL = getCollectionCEL(collection, root=root)
        node = createOpScript(collection, Constants.ASSIGN_OPSCRIPT, colCEL)
        nodes.append(node)
        if stack and not doesCollectionExistInStack(collection, stack, userGroup=True):
            stack.buildChildNode(node)

    return nodes


def createOverrideOpScripts(preAssignedDict, stack=None, root="/root"):
    clearStack(stack)
    nodes = []
    for collection, preAssignedMats in preAssignedDict.items():
        for material in preAssignedMats:
            invColCEL = getInverseCollectionCEL(collection, root=root, material=material)
            node = createOpScript(collection, Constants.OVERRIDE_OPSCRIPT, invColCEL)
            nodes.append(node)
            if stack:
                stack.buildChildNode(node)

    return nodes


def editColour(collection, colour, parentNode):
    asStack = SuperToolUtils.GetRefNode(parentNode, Constants.ATTRSET_KEY)
    asNode = doesCollectionExistInStack(collection, asStack)
    for idx, component in enumerate(colour):
        asNode.getParameter("groupValue.colour.i{}".format(idx)).setValue(component, 0.0)

    mcStack = SuperToolUtils.GetRefNode(parentNode, Constants.MAT_KEY)
    mcNode = doesCollectionExistInStack(collection, mcStack)
    for idx, component in enumerate(colour):
        mcNode.getParameter("shaders.hydraSurfaceParams.katanaColor.value.i{}".format(idx)).setValue(component, 0.0)



