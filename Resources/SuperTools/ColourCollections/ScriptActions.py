import random

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
            return True

    return False


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


# def assignMaterial(collection, material, materialsRoot="/root/materials", collectionsRoot="/root"):
#     maNode = NodegraphAPI.CreateNode("MaterialAssign", NodegraphAPI.GetRootNode())
#     maNode.getParameter("CEL").setValue("{}/${}".format(collectionsRoot, collection), 0.0)
#     maNode.getParameter("args.materialAssign.enable").setValue(True, 0.0)
#     maNode.getParameter("args.materialAssign.value").setValue("{}/{}".format(materialsRoot, material), 0.0)
#     return maNode
#
#
# def assignMaterials(collections, stack=None, collectionsRoot="/root"):
#     matAssignNodes = []
#     if stack:
#         # Delete nodes referencing no-longer-existing collections
#         for child in stack.getChildNodes():
#             if child.getParameter("CEL").getValue(0.0).split("$")[-1] not in collections:
#                 stack.deleteChildNode(child)
#     for collection in collections:
#         matAssignNode = assignMaterial(collection, Constants.COLMATERIAL.format(collection))
#         matAssignNodes.append(matAssignNode)
#         if stack and not doesCollectionExistInMaterialStack(collection, stack, root=collectionsRoot):
#             stack.buildChildNode(matAssignNode)
#
#     return matAssignNodes

def cleanUpStack(collections, stack, userGroup=False):
    # Delete nodes referencing no-longer-existing collections
    for child in stack.getChildNodes():
        paramName = "collection" if not userGroup else "user.collection"
        if child.getParameter(paramName).getValue(0.0) not in collections:
            stack.deleteChildNode(child)


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


def buildMaterials(collections, stack=None, node=None):
    nodes = []
    processedCollections = []
    for child in stack.getChildNodes():
        stack.deleteChildNode(child)

    client = getClient(node=node)
    for collection, attrs in collections.items():
        if "colour" not in attrs.keys():
            continue
        collectionPaths = GeoAPI.Util.CollectPathsFromCELStatement(client, attrs["cel"])
        for path in collectionPaths:
            cookedPath = client.cookLocation(path)
            if cookedPath.getAttrs() and cookedPath.getAttrs().getChildByName("materialAssign"):
                matAssign = cookedPath.getAttrs().getChildByName("materialAssign").getData()[0]
                if matAssign:
                    matAssign = matAssign.split("/root/materials/")[-1]  # Remove root to get namespace
                    name = matAssign.split("/")[-1]
                    namespace = matAssign.split(name)[0]

            elif collection not in processedCollections:
                processedCollections.append(collection)
                name = Constants.COLMATERIAL.format(collection)
                namespace = ""

            else:
                continue

            node = NodegraphAPI.CreateNode("Material", NodegraphAPI.GetRootNode())
            node.getParameter("name").setValue(name, 0.0)
            node.getParameter("namespace").setValue(namespace, 0.0)
            node.getParameters().createChildString("collection", collection)
            node.addShaderType("hydraSurface")
            node.getParameter("shaders.hydraSurfaceShader.enable").setValue(1.0, 0.0)
            node.getParameter("shaders.hydraSurfaceShader.value").setValue("katana_constant", 0.0)
            node.checkDynamicParameters()
            node.getParameter("shaders.hydraSurfaceParams.katanaColor.enable").setValue(1.0, 0.0)
            for idx, component in enumerate(attrs["colour"]):
                node.getParameter("shaders.hydraSurfaceParams.katanaColor.value.i{}".format(idx)).setValue(component, 0.0)
            nodes.append(node)
            if stack and not doesCollectionExistInStack(collection, stack):
                stack.buildChildNode(node)

    return nodes


def createOpScripts(collections, stack=None, root="/root"):
    nodes = []
    cleanUpStack(collections, stack, userGroup=True)
    for collection in collections:
        node = NodegraphAPI.CreateNode("OpScript", NodegraphAPI.GetRootNode())
        node.getParameter("CEL").setValue("{}/${}".format(root, collection), 0.0)
        node.getParameter("script.lua").setValue(Constants.OPSCRIPT, 0.0)
        node.getParameters().createChildGroup("user")
        node.getParameter("user").createChildString("collection", collection)
        nodes.append(node)
        if stack and not doesCollectionExistInStack(collection, stack, userGroup=True):
            stack.buildChildNode(node)

    return nodes




