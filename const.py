
configName = "dgConf.txt"
#currently only Graphics Resolution
modSettingsName = "dgSettings.txt"


#edit mode enums
EDIT_TILE = 0
EDIT_ENTITY = 1

#Entities which can only be spawned from parents
#used to determine if they crash the game or not
entityChildIds = [12, 16, 17, 33, 34, 36, 50, 51, 52, 53, 55, 57, 62, 71, 77, 78, 79, 80, 82, 89, 95, 101, 103, 109, 110, 112, 113]
#total entity ids
entityFuncCount = 121

#window types
WINDOW_NONE = 0
WINDOW_TILEPALETTE = 1
WINDOW_ENTITYPALETTE = 2
WINDOW_TOOLS = 3
WINDOW_TOOLTIP = 4

#TODO... really gotta find somewhere good to put this
tileScale = 1
tileWidth = 16 * tileScale


#undo thing
UNDO_TILE = 0
UNDO_ENTITY_ADD = 1
UNDO_ENTITY_REMOVE = 2
UNDO_ENTITY_MODIFY = 3