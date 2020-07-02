from enum import Enum
# a  settlement/city class

class BuildingType(Enum):
    Settlement = 0
    Road = 1
    City = 2
    def __repr__(self):
      return self.name
    def dict(self):
      return self.name

class Building:
    def __init__(self, owner, type):
      # sets the owner and type
      self.owner = owner
      self.type = type

class Road(Building):
    def __init__(self, owner, point_one, point_two):
      super(Road, self).__init__(owner, BuildingType.Road)
      self.point_one = point_one
      self.point_two = point_two

    def __repr__(self):
      return "Road, owned by player %s, from %s to %s" % (self.owner, self.point_one.position, self.point_two.position)

    def dict(self):
      return {"type":self.type, "owner":self.owner, "point_one":self.point_one, "point_two":self.point_two}

class Settlement(Building):
    def __init__(self, owner, point):
      super(Settlement, self).__init__(owner, BuildingType.Settlement)
      self.point = point
      
    def __repr__(self):
      return "Settlement, owned by player %s" % self.owner

    def dict(self):
        return {"type":self.type, "owner":self.owner, "point":self.point}

class City(Building):
    def __init__(self, owner, point):
      super(City, self).__init__(owner, BuildingType.City)
      self.point = point
      
    def __repr__(self):
      return "City, owned by player %s" % self.owner

    def dict(self):
        return {"type":self.type, "owner":self.owner, "point":self.point}
