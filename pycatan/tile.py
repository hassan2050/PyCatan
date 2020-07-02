from pycatan.tile_type import TileType
from pycatan.point import Point

class Tile:
    def __init__(self, type, token_num, position, points):
        self.type = type
        self.token_num = token_num
        self.position = position
        self.points = points

    def __repr__(self):
        return "<%s %s at %s>" % (self.type.name, self.token_num, self.position)
