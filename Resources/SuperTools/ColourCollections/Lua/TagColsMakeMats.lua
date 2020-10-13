collectionsAttr = Interface.GetAttr('collections')
if collectionsAttr ~= nil then
    sscb = OpArgsBuilders.StaticSceneCreate(true)
    for i=0,(collectionsAttr:getNumberOfChildren()-1) do
        colName = collectionsAttr:getChildName(i)
        if Interface.GetAttr("collections."..colName..".viewer") ~= nil then
            colMat = Interface.GetAttr("collections."..colName..".viewer.material")
            if colMat == nil then
                Interface.SetAttr("collections."..colName..".viewer.material", StringAttribute(colName.."ColMAT"))
            end
            colColour = Interface.GetAttr("collections."..colName..".viewer.colour")
            colMat = Interface.GetOutputAttr("collections."..colName..".viewer.material")
            matRoot = '/root/materials/'..colMat:getValue()
            -- Build material if it does not exist
            if Interface.DoesLocationExist(matRoot) == false and Interface.GetAttr("collections."..colName..".cel") ~= nil then
                sscb:createEmptyLocation(matRoot, "material")
                sscb:setAttrAtLocation(matRoot, "material.hydraSurfaceShader", StringAttribute("katana_constant"))
                sscb:setAttrAtLocation(matRoot, "material.hydraSurfaceParams.katanaColor", colColour)

            -- If it already exists, query its colour attribute
            else
                matAttr=InterfaceUtils.CookDaps('material', matRoot)
                colColour = matAttr:getChildByName('material.hydraSurfaceParams.katanaColor')
            end
            Interface.SetAttr("collections."..colName..".viewer.colour", colColour)
        end
    end
    Interface.ExecOp("StaticSceneCreate", sscb:build())
end
