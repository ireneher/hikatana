# PARAMETERS
VERSION_PARAM = "version"
CURRENT_VERSION = 1
LOCATION_PARAM = "location"
DEFAULT_LOCATION = "/root"
ASSIGN_OPSCRIPT = "root = os.getenv('HIKATANA_ROOT')\ndofile(PathUtils.Join(root,'Resources/SuperTools/ColourCollections/Lua/AssignMaterials.lua'))"
OVERRIDE_OPSCRIPT = "root = os.getenv('HIKATANA_ROOT')\ndofile(PathUtils.Join(root,'Resources/SuperTools/ColourCollections/Lua/OverrideMaterials.lua'))"

#NODES
DOT_KEY = "dotNode"
ATTRSET_KEY = "attrSetStackNode"
MAT_KEY = "materialStackNode"
OPSCRIPT_ASSIGN_KEY = "opscriptAssignStackNode"
OPSCRIPT_OVERRIDE_KEY = "opscriptOverrideStackNode"
MERGE_NODE_KEY = "mergeNode"

DEFAULT_MAT_LOCATION = "/root/materials"
COLMATERIAL = "{}ColMAT"

