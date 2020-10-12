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


def cookCollections(root="/root", node=None, namesOnly=True):
    client = getClient(node=node)
    cookedLoc = client.cookLocation(root)
    collectionsAttr = cookedLoc.getAttrs().getChildByName("collections")
    attrDict = {}
    cookedCols = {}
    if collectionsAttr:
        if namesOnly:
            return [colName for (colName, _) in collectionsAttr.childList()]
        else:
            for (colName, colAttr) in collectionsAttr.childList():
                for (attrName, attr) in colAttr.childList():
                    if isinstance(attr, FnAttribute.GroupAttribute):
                        for (subattrName, subAttr) in attr.childList():
                            attrDict[subattrName] = subAttr.getNearestSample(0.0)
                    else:
                        attrDict[attrName] = attr.getNearestSample(0.0)
                cookedCols.setdefault(colName, {}).update(attrDict)

    return cookedCols


def randomComponent():
    return random.random()


def setColourAttribute(collection):
    asNode = NodegraphAPI.CreateNode("AttributeSet", NodegraphAPI.GetRootNode())
    asNode.getParameter("celSelection").setValue("/root", 0.0)
    asNode.getParameter("mode").setValue("CEL", 0.0)
    asNode.getParameter("attributeName").setValue("collections.{}.viewer".format(collection), 0.0)
    asNode.getParameter("attributeType").setValue("group", 0.0)
    asNode.getParameter("groupValue").createChildNumberArray("colour", 4)
    asNode.getParameter("groupValue.colour.i0").setValue(randomComponent(), 0.0)
    asNode.getParameter("groupValue.colour.i1").setValue(randomComponent(), 0.0)
    asNode.getParameter("groupValue.colour.i2").setValue(randomComponent(), 0.0)
    asNode.getParameter("groupValue.colour.i3").setValue(1.0, 0.0)
    return asNode


def assignMaterial(collection, material, materialsRoot="/root/materials"):
    maNode = NodegraphAPI.CreateNode("MaterialAssign", NodegraphAPI.GetRootNode())
    maNode.getParameter("CEL").setValue("/${}".format(collection), 0.0)
    maNode.getParameter("args.materialAssign.enable").setValue(True, 0.0)
    maNode.getParameter("args.materialAssign.value").setValue("{}/{}".format(materialsRoot, material), 0.0)
    return maNode


def assignMaterials(collections, stack=None):
    matAssignNodes = []
    for collection in collections:
        matAssignNode = assignMaterial(collection, Constants.COLMATERIAL.format(collection))
        matAssignNodes.append(matAssignNode)
        if stack:
            stack.buildChildNode(matAssignNode)

    return matAssignNodes


def setColourAttributes(collections, stack=None):
    attrSetNodes = []
    for collection in collections:
        attrSetNode = setColourAttribute(collection)
        attrSetNodes.append(attrSetNode)
        if stack:
            stack.buildChildNode(attrSetNode)

    return attrSetNodes


