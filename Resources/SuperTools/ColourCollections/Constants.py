# PARAMETERS
VERSION_PARAM = "version"
CURRENT_VERSION = 1
LOCATION_PARAM = "location"
DEFAULT_LOCATION = "/root"
OPSCRIPT = "root = os.getenv('HIKATANA_ROOT')\ndofile(PathUtils.Join(root,'Resources/SuperTools/ColourCollections/Lua/AssignMaterials.lua'))"

#NODES
DOT_KEY = "dotNode"
ATTRSET_KEY = "attrSetStackNode"
MAT_KEY = "materialStackNode"
OPSCRIPT_KEY = "opscriptNode"
MERGE_NODE_KEY = "mergeNode"

DEFAULT_MAT_LOCATION = "/root/materials"
COLMATERIAL = "{}ColMAT"
