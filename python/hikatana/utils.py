from Katana import FnGeolib, Nodes3DAPI, NodegraphAPI
import time, GeoAPI
from GeoAPI_cmodule import GeometryProducer
from GeoAPI.Manifest import FnGeolib, FnAttribute


def getClient(node=None):
    runtime = FnGeolib.GetRegisteredRuntimeInstance()
    transaction = runtime.createTransaction()
    client = transaction.createClient()
    if node:
        terminalOp = Nodes3DAPI.GetOp(transaction, node)
        transaction.setClientOp(client, terminalOp)
        runtime.commit(transaction)
    return client


# Nearly identical to the Foundry's implementation of CollectPathsFromCELStatement
# except this also returns the location data, useful for further checks/processing
# without having to recook
def CollectLocationsFromCELStatement(producerOrClient, celStatement, interruptCallback=None):
    if isinstance(producerOrClient, GeometryProducer):
        origClient = producerOrClient.getClient()
    else:
        origClient = producerOrClient
    if not isinstance(origClient, FnGeolib.GeolibRuntimeClient):
        raise ValueError, 'First arg must be a GeometryProducer or ' + 'FnGeolib.GeolibRuntimeClient object'
    result = []
    runtime = FnGeolib.GetRegisteredRuntimeInstance()
    txn = runtime.createTransaction()
    sourceOp = origClient.getOp()
    if sourceOp:
        matchOp = txn.createOp()
        txn.setOpArgs(matchOp, 'CelMatch', FnAttribute.GroupBuilder().set('CEL', FnAttribute.StringAttribute(celStatement)).build())
        txn.setOpInputs(matchOp, (sourceOp,))
        client = txn.createClient()
        txn.setClientOp(client, matchOp)
        runtime.commit(txn)
        lastTime = time.time()
        traversal = FnGeolib.Util.Traversal(client, '/root')
        while traversal.valid():
            if interruptCallback:
                curTime = time.time()
                if curTime - lastTime > 0.25:
                    lastTime = curTime
                    if interruptCallback(len(result), curTime):
                        return result
            matchAttr = traversal.getLocationData().getAttrs().getChildByName('__celMatch')
            if isinstance(matchAttr, FnAttribute.IntAttribute):
                if matchAttr.getValue(0, False):
                    result.append((traversal.getLocationPath(), traversal.getLocationData()))
            canMatchChildrenAttr = traversal.getLocationData().getAttrs().getChildByName('__celCanMatchChildren')
            if isinstance(canMatchChildrenAttr, FnAttribute.IntAttribute):
                if canMatchChildrenAttr.getValue(1, False) == 0:
                    traversal.skipChildren()
            traversal.next()

        return result
