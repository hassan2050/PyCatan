from pycatan.harbor import Harbor, HarborType
from pycatan.player import Player
from pycatan.statuses import Statuses
from pycatan.building import *
from pycatan.tile_type import TileType
from pycatan.card import ResCard, DevCard
from pycatan.tile import Tile
from pycatan.point import Point

import logging

# used to shuffle the deck of tiles
import random

import abc

# used for debugging
import pprint

# Base class for different Catan boards
# Should not be instantiated, otherwise the board will be empty
class Board(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, game):
        # The game the board is in
        self.game = game
        # The tiles on the board
        # Should be set in a subclass
        self.tiles = ()
        # The points on the board
        # Where the players can place settlements/cities
        # Will be set at the end of __init__
        self.points = ()
        # The roads
        self.roads = []
        # The locations of the harbors
        self.harbors = []
        # The location of the robber
        # going r, i
        self.robber = None

    @staticmethod
    def get_tile_indexes_for_point(r, i):
      pass

    def get_connected_points(self, r, i):
      pass

    @staticmethod
    def get_outside_points():
      pass

    # gives the players cards for a certain roll
    def add_yield(self, roll):

        for r in self.points:
            for p in r:
                # Check there is a building on the point
                if p.building != None:
                    building = p.building
                    tiles = p.tiles

                    # checks if any tiles have the right number
                    for current_tile in tiles:

                        #logging.debug("Robber %s %s" % (self.robber, current_tile))
                        # makes sure the robber isn't there
                        if self.robber is current_tile:
                            # skips this tile
                            continue

                        if current_tile.token_num == roll:
                            # adds the card to the player's inventory
                            owner = building.owner
                            # gets the card type
                            card_type = Board.get_card_from_tile(current_tile.type)
                            # adds two if it is a city
                            if building.type == BuildingType.City:
                                self.game.players[owner].add_cards([
                                    card_type,
                                    card_type
                                ])

                            else:
                                self.game.players[owner].add_cards([
                                    card_type
                                ])


    # adds a Building object to the board
    def add_building(self, building, point):
        point.building = building

    # adds a Building object, which must be a road
    # since roads record their own position and are not in self.points
    def add_road(self, road):
        self.roads.append(road)

    def get_road(self, p1, p2):
      for r in self.roads:
        if (r.point_one == p1 and r.point_two == p2):
          return r
        if (r.point_one == p2 and r.point_two == p1):
          return r
      return None

    # upgrades an existing settlement to a city
    def upgrade_settlement(self, player, point):
        if player.num_cities == 0: return Statuses.ERR_OUTOFBUILDINGS

        # Get building at point
        building = point.building

        # checks there is a settlement at r, i
        if building == None:
            return Statuses.ERR_NOT_EXIST

        # checks the settlement is controlled by the correct player
        # if no player is specified, uses the current controlling player
        if building.owner != player.get_num():
            return Statuses.ERR_BAD_OWNER

        # checks it is a settlement and not a city
        if building.type != BuildingType.Settlement:
            return Statuses.ERR_UPGRADE_CITY

        # checks the player has the cards
        needed_cards = [
            ResCard.Wheat,
            ResCard.Wheat,
            ResCard.Ore,
            ResCard.Ore,
            ResCard.Ore
        ]
        if not player.has_cards(needed_cards):
            return Statuses.ERR_CARDS

        # removes the cards
        player.remove_cards(needed_cards)
        # changes the settlement to a city
        point.building = City(building.owner, building.point)
        building = point.building

        # adds another victory point
        player.victory_points += 1

        player.num_cities -= 1
        player.num_settlements += 1

        return Statuses.ALL_GOOD

    # gets all the buildings on the board
    def get_buildings(self):

        buildings = []
        for r in self.points:
            for p in r:
                if p.building != None:
                    buildings.append(p.building)

        return buildings

    # moves the robber to a given coord
    def move_robber(self, tile_pos):
        self.robber = tile_pos

    def __repr__(self):
        return ("Board Object")

    # Get a shuffled deck of the correct number of each type of tile in a board
    @staticmethod
    def get_shuffled_tile_deck():
        deck = []
        # sets up all_tiles
        for i in range(4):

            # adds four fields, forests and pastures
            deck.append(TileType.Fields)
            deck.append(TileType.Forest)
            deck.append(TileType.Pasture)
            # adds three mountains and hills
            if i < 3:
                deck.append(TileType.Mountains)
                deck.append(TileType.Hills)

            # adds one desert
            if i == 0:
                deck.append(TileType.Desert)

        # shuffles the deck
        random.shuffle(deck)
        return deck

    @staticmethod
    def get_shuffled_tile_nums():
        nums = []
        # Get 2 of each number, most of the time
        for i in range(2):
            # Go through each type
            for x in range(2, 13):
                # Does not add a number token with 7
                if x != 7:
                    # Only adds one 2 and one 12
                    if x == 2 or x == 12:
                        if i == 0:
                            nums.append(x)
                    # Adds two of everything else
                    else:
                        nums.append(x)
        random.shuffle(nums)
        return nums

    # returns the card associated with the tile
    # for example, Brick for Hills, Wood for forests, etc
    @staticmethod
    def get_card_from_tile(tile):

        # returns the appropriete card
        if tile == TileType.Forest:
            return ResCard.Wood

        elif tile == TileType.Hills:
            return ResCard.Brick

        elif tile == TileType.Pasture:
            return ResCard.Sheep

        elif tile == TileType.Fields:
            return ResCard.Wheat

        elif tile == TileType.Mountains:
            return ResCard.Ore

        else:
            return None

    def get_all_tiles(self):
      return [item for sublist in self.game.board.tiles for item in sublist]

    def get_all_points(self):
      return [item for sublist in self.game.board.points for item in sublist]

    def dict(self):
      d = {}

      d['tiles'] = self.get_all_tiles()
      d['harbors'] = self.harbors
      d['robber'] = self.robber.position
      d['buildings'] = self.get_buildings()
      d['roads'] = self.roads

      return d

    def load(self, d):
      for tile_data in d['tiles']:
        t = self.game.get_tile(tile_data['position'])
        t.token_num = tile_data['token_num']
        t.type = getattr(TileType, tile_data['type'])
          
      bpoints = self.get_all_points()
      for point in bpoints:
        point.building = None

      self.robber = self.game.get_tile(d['robber'])

      for building_data in d['buildings']:
        if building_data['type'] == "Settlement":
          p = self.game.get_point(building_data['point'])
          p.building = Settlement(building_data['owner'], p)
        elif building_data['type'] == "City":
          p = self.game.get_point(building_data['point'])
          p.building = City(building_data['owner'], p)

      for road_data in d['roads']:
        p1 = self.game.get_point(road_data['point_one'])
        p2 = self.game.get_point(road_data['point_two'])
        self.roads.append(Road(road_data['owner'], p1, p2))
          
