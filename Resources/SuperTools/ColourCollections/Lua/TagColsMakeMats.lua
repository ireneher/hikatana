collectionsAttr = Interface.GetAttr('collections')
if collectionsAttr ~= nil then
    for i=0,(collectionsAttr:getNumberOfChildren()-1) do
        colName = collectionsAttr:getChildName(i)
        colAttr = collectionsAttr:getChildByIndex(i)
        colCEL = colAttr:getChildByIndex(0):getValue()
        colMat = Interface.GetAttr("collections."..colName..".material")
        if colMat == nil then
            Interface.SetAttr("collections."..colName..".material", StringAttribute(colName.."MAT"))
        end
        colColour = Interface.GetAttr("collections."..colName..".colour")
        colMat = Interface.GetOutputAttr("collections."..colName..".material")
        matRoot = '/root/materials/'..colMat:getValue()
        if Interface.DoesLocationExist(matRoot) == true then
            matAttr=InterfaceUtils.CookDaps('material',matRoot)
            matColour = Interface.GetAttr('material.hydraSurfaceParams.katanaColor',matRoot)
            Interface.SetAttr("collections."..colName..".colour", matColour)
        else
            sscb = OpArgsBuilders.StaticSceneCreate(true)
            sscb:createEmptyLocation(matRoot, "material")
            sscb:setAttrAtLocation(matRoot, "material.hydraSurfaceShader", StringAttribute("katana_constant"))
            sscb:setAttrAtLocation(matRoot, "material.hydraSurfaceParams.katanaColor", FloatAttribute({math.random(),math.random(), math.random(), 1.0}))
            Interface.ExecOp("StaticSceneCreate", sscb:build())
        end
    end
end
