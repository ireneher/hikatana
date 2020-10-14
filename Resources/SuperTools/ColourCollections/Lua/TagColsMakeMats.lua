local matAssign = Interface.GetAttr('materialAssign')
local collection = Interface.GetOpArg('user.collection'):getValue()
print(collection)
if matAssign ~= nil then
    matRoot = matAssign:getValue()
else
    matRoot = '/root/'..collection..'MAT'
    Interface.SetAttr('materialAssign', StringAttribute(matRoot))
end

sscb = OpArgsBuilders.StaticSceneCreate(true)
sscb:createEmptyLocation(matRoot, "material")
sscb:setAttrAtLocation(matRoot, "material.hydraSurfaceShader", StringAttribute("katana_constant"))
sscb:setAttrAtLocation(matRoot, "material.hydraSurfaceParams.katanaColor", colColour)
--Interface.SetAttr("collections."..colName..".viewer.colour", colColour)
Interface.ExecOp("StaticSceneCreate", sscb:build())


