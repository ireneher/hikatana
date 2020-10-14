local collection = Interface.GetOpArg('user.collection'):getValue()
local matAssign = Interface.GetAttr('materialAssign')
if matAssign == nil then
    Interface.SetAttr('materialAssign', StringAttribute('/root/materials/'..collection..'ColMAT'))
end