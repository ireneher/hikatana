import Katana

import Node


def GetEditor():
    from Editor import ColourCollectionsEditor

    return ColourCollectionsEditor


if Node:
    PluginRegistry = [
        (
            "SuperTool",
            2,
            "HIColourCollections",
            (Node.ColourCollectionsNode, GetEditor),
        ),
    ]
