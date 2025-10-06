
class Entity:
    def __init__(self, id, x, y, flags=0, event=0):
        self.id = id
        self.x = x
        self.y = y
        self.flags = flags
        self.event = event
        self.attributes = {}

class Layer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[0] * width for _ in range(height)]

class Stage:
    def __init__(self, name, width=0, height=0):
        self.name = name
        self.width = width
        self.height = height
        self.layers = {
            'background': None,
            'foreground': None,
            'collision': None,
        }
        self.entities = []
