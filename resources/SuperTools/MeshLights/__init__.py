import v1 as MeshLights

if MeshLights:
    PluginRegistry = [
        (
            "SuperTool",
            2,
            "HIMeshLights",
            (MeshLights.Node.MeshLightsNode, MeshLights.GetEditor),
        ),
    ]