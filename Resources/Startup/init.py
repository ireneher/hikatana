from Katana import Utils, Callbacks, NodegraphAPI

#import SuperTools.ColourCollections.ScriptActions as CCSA

def isNodeViewed(nodeName):
    from Katana import NodegraphAPI
    return NodegraphAPI.IsNodeViewed(NodegraphAPI.GetNode(nodeName))

NodegraphAPI.SetExpressionGlobalValue("isNodeViewed", isNodeViewed)

#Utils.EventModule.RegisterCollapsedHandler(CCSA.onNewCollection, eventType="parameter_finalizeValue")


