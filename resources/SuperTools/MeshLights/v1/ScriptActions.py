import os

from Katana import GeoAPI

from hikatana import utils


def createMeshLights(gafferNode, celExpression, lightName="", rigName="", mode="Append"):
    client = utils.getClient(node=gafferNode)
    collectedLocations = GeoAPI.Util.CelUtil.CollectPathsFromCELStatement(client, celExpression)

    rootPackage = gafferNode.getRootPackage()
    if mode == "Override":
        for package in rootPackage.getChildPackages():
            package.delete()

    rigPackage = rootPackage.createChildPackage("RigPackage", rigName or "MeshLightsRig")
    mmPackage = rootPackage.createChildPackage("MasterMaterialPackage", "{}MasterMaterial".format(rigName))
    mmPackage.setShader("arnoldLight", "mesh_light")

    for idx, location in enumerate(collectedLocations):
        cookedLocation = client.cookLocation(location)
        if cookedLocation.getAttrs().getChildByName("type").getValue() not in ("subdmesh", "polymesh"):
            continue
        name = lightName or "{}Light".format(os.path.basename(location))
        lightPackage = rigPackage.createChildPackage("LightPackage", "{}_{}".format(name, idx))
        lightPackage.setMasterMaterial(mmPackage)
        materialNode = lightPackage.getMaterialNode()
        materialNode.checkDynamicParameters()
        materialNode.getParameter('shaders.arnoldLightParams.mesh.enable').setValue(True, 0.0)
        materialNode.getParameter('shaders.arnoldLightParams.mesh.value').setValue(location, 0.0)

