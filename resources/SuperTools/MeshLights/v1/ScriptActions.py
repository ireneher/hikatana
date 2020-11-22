import os

from Katana import GeoAPI, Nodes3DAPI

from hikatana import utils


def createMeshLights(gafferNode, celExpression, lightName="", rigName="", mode="Append", lightType="mesh"):
    client = utils.getClient(node=gafferNode)
    geoProducer = Nodes3DAPI.GetGeometryProducer(gafferNode)
    collectedLocations = GeoAPI.Util.CelUtil.CollectPathsFromCELStatement(client, celExpression)

    rootPackage = gafferNode.getRootPackage()
    if mode == "Override":
        for package in rootPackage.getChildPackages():
            package.delete()

    rigName = rigName or "{}LightsRig".format(lightType)
    rigPackage = rootPackage.createChildPackage("RigPackage", rigName)
    mmPackage = rootPackage.createChildPackage("MasterMaterialPackage", "{}MasterMaterial".format(rigName))
    mmPackage.setShader("arnoldLight", "{}_light".format(lightType))

    for idx, location in enumerate(collectedLocations):
        cookedLocation = client.cookLocation(location)
        if cookedLocation.getAttrs().getChildByName("type").getValue() not in ("subdmesh", "polymesh"):
            continue
        name = lightName or "{}Light".format(os.path.basename(location))
        lightPackage = rigPackage.createChildPackage("LightPackage", "{}_{}".format(name, idx))
        lightPackage.setMasterMaterial(mmPackage)
        materialNode = lightPackage.getMaterialNode()
        materialNode.checkDynamicParameters()
        if lightType == "mesh":
            materialNode.getParameter('shaders.arnoldLightParams.mesh.enable').setValue(True, 0.0)
            materialNode.getParameter('shaders.arnoldLightParams.mesh.value').setValue(location, 0.0)
        elif lightType == "point":
            bounds = GeoAPI.Transform.ProducerWorldBounds(geoProducer.getProducerByPath(location))
            centerX = (bounds[0] + bounds[1]) / 2
            centerY = (bounds[2] + bounds[3]) / 2
            centerZ = (bounds[4] + bounds[5]) / 2
            materialNode.getParameter('shaders.arnoldLightParams.position.enable').setValue(True, 0.0)
            materialNode.getParameter('shaders.arnoldLightParams.position.value.i0').setValue(centerX, 0.0)
            materialNode.getParameter('shaders.arnoldLightParams.position.value.i1').setValue(centerY, 0.0)
            materialNode.getParameter('shaders.arnoldLightParams.position.value.i2').setValue(centerZ, 0.0)


