from enum import Enum

# The different types of resource cards
class ResCard(Enum):

    # the resource cards
    Wood = 0
    Brick = 1
    Ore = 2
    Sheep = 3
    Wheat = 4
    def __repr__(self):
      return self.name
    def dict(self): return self.name

settlementBuild = (ResCard.Wood, ResCard.Brick, ResCard.Sheep, ResCard.Wheat)
cityBuild = (ResCard.Ore, ResCard.Ore, ResCard.Ore, ResCard.Wheat, ResCard.Wheat)
devBuild = (ResCard.Wheat, ResCard.Sheep, ResCard.Ore)
roadBuild = (ResCard.Wood, ResCard.Brick)

# The different types of developement cards
class DevCard(Enum):

    # the developement cards
    Road = 0
    VictoryPoint = 1
    Knight = 2
    Monopoly = 3
    YearOfPlenty = 4
    def __repr__(self):
      return self.name
    def dict(self): return self.name
