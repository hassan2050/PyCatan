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

    def dict(self):
      return {"type":self.type.name, "token_num":self.token_num, "position":self.position}


    def prob(self):
      if self.token_num in (2,12): return .03
      if self.token_num in (3,11): return .06
      if self.token_num in (4,10): return .08
      if self.token_num in (5,9): return .11
      if self.token_num in (6,8): return .14
      return .0
