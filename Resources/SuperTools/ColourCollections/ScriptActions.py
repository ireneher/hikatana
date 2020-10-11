import os
import sys

from Katana import FnGeolib, Nodes3DAPI, NodegraphAPI


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
    cookedLoc = client.cookLocation(root)
    collectionsAttr = cookedLoc.getAttrs().getChildByName("collections")
    attrDict = {}
    cookedCols = {}
    if collectionsAttr:
        for (colName, colAttr) in collectionsAttr.childList():
            for (attrName, attr) in colAttr.childList():
                attrDict[attrName] = attr.getValue()
            cookedCols.setdefault(colName, {}).update(attrDict)

    return cookedCols


def assignMaterialtoCollection(collection, material, materialsRoot="/root/materials"):
    maNode = NodegraphAPI.CreateNode("MaterialAssign")
    maNode.getParameter("CEL").setValue("/${}".format(collection), 0.0)
    maNode.getParameter("materialAssign").setValue("{}/{}".format(materialsRoot, material), 0.0)
    return maNode


def cookCollectionsMaterialAssign(root="/root", node=None, stack=None):
    cookedCols = cookCollections(root=root, node=node)
    matAssignNodes = []
    for collection, attributes in cookedCols.items():
        matAssignNode = assignMaterialtoCollection(collection, attributes["material"])
        matAssignNodes.append(matAssignNode)
        if stack:
            stack.buildChildNode(matAssignNode)

    return matAssignNodes
