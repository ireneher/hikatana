import random

from Katana import FnGeolib, Nodes3DAPI, NodegraphAPI, FnAttribute

import Constants


def getClient(node=None):
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
    Nodes3DAPI.CommitChanges()
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


def doesCollectionExistInMaterialStack(collection, stack, root="/root"):
    for existingChildNode in stack.getChildNodes():
        if existingChildNode.getParameter("CEL").getValue(0.0) == "{}/${}".format(root, collection):
            return True

    return False


def doesCollectionExistInAttributeStack(collection, stack):
    for existingChildNode in stack.getChildNodes():
        if existingChildNode.getParameter("attributeName").getValue(0.0) == "collections.{}.viewer".format(collection):
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

    return asNode


def assignMaterial(collection, material, materialsRoot="/root/materials", collectionsRoot="/root"):
    maNode = NodegraphAPI.CreateNode("MaterialAssign", NodegraphAPI.GetRootNode())
    maNode.getParameter("CEL").setValue("{}/${}".format(collectionsRoot, collection), 0.0)
    maNode.getParameter("args.materialAssign.enable").setValue(True, 0.0)
    maNode.getParameter("args.materialAssign.value").setValue("{}/{}".format(materialsRoot, material), 0.0)
    return maNode


def assignMaterials(collections, stack=None, collectionsRoot="/root"):
    matAssignNodes = []
    if stack:
        # Delete nodes referencing no-longer-existing collections
        for child in stack.getChildNodes():
            if child.getParameter("CEL").getValue(0.0).split("$")[-1] not in collections:
                stack.deleteChildNode(child)
    for collection in collections:
        matAssignNode = assignMaterial(collection, Constants.COLMATERIAL.format(collection))
        matAssignNodes.append(matAssignNode)
        if stack and not doesCollectionExistInMaterialStack(collection, stack, root=collectionsRoot):
            stack.buildChildNode(matAssignNode)

    return matAssignNodes


def setColourAttributes(collections, stack=None, root="/root"):
    attrSetNodes = []
    if stack:
        # Delete nodes referencing no-longer-existing collections
        for child in stack.getChildNodes():
            if child.getParameter("attributeName").getValue(0.0).split(".")[1] not in collections:
                stack.deleteChildNode(child)
    for collection in collections:
        attrSetNode = setColourAttribute(collection, root=root)
        attrSetNodes.append(attrSetNode)
        if stack and not doesCollectionExistInAttributeStack(collection, stack):
            stack.buildChildNode(attrSetNode)

    return attrSetNodes


