class Point:
    def __init__(self, tiles, position):
        self.tiles = tiles
        self.building = None
        self.position = position
        self.connected_points = None

    def __repr__(self):
        return "Point(%s,%s)" % (self.position[0], self.position[1])

