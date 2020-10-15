import v1 as ColourCollections

if ColourCollections:
    PluginRegistry = [
        (
            "SuperTool",
            2,
            "HIColourCollections",
            (ColourCollections.Node.ColourCollectionsNode, ColourCollections.GetEditor),
        ),
    ]