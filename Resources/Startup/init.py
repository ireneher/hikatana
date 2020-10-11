from Katana import NodegraphAPI


def isNodeViewed(nodeName):
    from Katana import NodegraphAPI
    return NodegraphAPI.IsNodeViewed(NodegraphAPI.GetNode(nodeName))

NodegraphAPI.SetExpressionGlobalValue("isNodeViewed", isNodeViewed)
