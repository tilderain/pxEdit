
configName = "dgConf.txt"
#currently only Graphics Resolution
modSettingsName = "dgSettings.txt"


#edit mode enums
EDIT_TILE = 0
EDIT_ENTITY = 1

#Entities which can only be spawned from parents
#used to determine if they crash the game or not
entityCrashIds = [12, 16, 17, 33, 34, 36, 50, 51, 52, 53, 55, 57, 62, 71, 77, 78, 79, 80, 82, 89, 95, 101, 103, 109, 110, 112, 113]
#total entity ids
entityFuncCount = 122

#for a green title color
entityGoodIds = [1, 2, 3, 4, 7, 37, 45, 47, 60, 61, 64, 74, 75, 91, 92, 96, 116, 119, 121]
#utility invisible entities for orange
entityUtilIds = [6, 19, 22, 38, 46, 56, 70, 73, 87, 93, 99, 106, 107, 117, 118]

#window types
WINDOW_NONE = 0
WINDOW_TILEPALETTE = 1
WINDOW_ENTITYPALETTE = 2
WINDOW_TOOLS = 3
WINDOW_TOOLTIP = 4
WINDOW_ENTITYEDIT = 5

STYLE_TOOLTIP_BLACK = 0
STYLE_TOOLTIP_YELLOW = 1

TEXTINPUTTYPE_NORMAL = 0
TEXTINPUTTYPE_NUMBER = 1

#TODO... really gotta find somewhere good to put this
tileScale = 1
tileWidth = 16 * tileScale


#undo thing
UNDO_TILE = 0
UNDO_ENTITY_ADD = 1
UNDO_ENTITY_REMOVE = 2
UNDO_ENTITY_MOVE = 3

#multi
MULTIPLAYER_NONE = 0
MULTIPLAYER_HOST = 1
MULTIPLAYER_CLIENT = 2