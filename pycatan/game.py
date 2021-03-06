from pycatan.default_board import DefaultBoard
from pycatan.player import Player
from pycatan.statuses import Statuses
from pycatan.card import ResCard, DevCard
from pycatan.building import *
from pycatan.harbor import Harbor

import json
import logging
import random
import math

class CatanError(Exception):
  def __init__(self, errcode):
    self.errcode = errcode

class Game:

    # initializes the  game
    def __init__(self, log=None, num_of_players=3, on_win=None, starting_board=False, points_to_win=10):
        self.log = log
        # creates a board
        self.board = DefaultBoard(game=self);
        # creates players
        self.players = []
        for i in range(num_of_players):
            self.players.append(Player(num=i, game=self))
        self.currentPlayer = None

        self.points_to_win = points_to_win
        # Set onWin method
        self.on_win = on_win
        # creates a new Developement deck
        self.dev_deck = []
        for i in range(14):
            # Add 2 Road, Monopoly and Year of Plenty cards
            if i < 2:
                self.dev_deck.append(DevCard.Road)
                self.dev_deck.append(DevCard.Monopoly)
                self.dev_deck.append(DevCard.YearOfPlenty)
            # Add 5 Victory Point cards
            if i < 5:
                self.dev_deck.append(DevCard.VictoryPoint)
            # Add 14 knight cards
            self.dev_deck.append(DevCard.Knight)
        # Shuffle the developement deck
        random.shuffle(self.dev_deck)
        # the longest road owner and largest army owner
        self.longest_road_owner = None
        self.largest_army = None
        # whether the game has finished or not
        self.has_ended = False
        self.winner = None


    # creates a new settlement belong to the player at the coodinates
    def add_settlement(self, player, point, is_starting=False):
        # builds the settlement
        status = player.build_settlement(point=point, is_starting=is_starting)
        # If successful, check if the player has now won
        if status == Statuses.ALL_GOOD:
          if self.log: self.log.log_player_buys_settlement(player, point)
          self.check_for_win()

        return status

    # builds a road going from point start to point end
    def add_road(self, player, start, end, is_starting=False):
        # builds the road
        stat = player.build_road(start=start, end=end, is_starting=is_starting)
        # checks for a new longest road segment
        if self.log: self.log.log_player_buys_road(player, start, end)
        self.set_longest_road()
        # returns the status
        return stat

    # builds a new developement cards for the player
    def build_dev(self, player):
        # makes sure there is still at least one development card left
        if len(self.dev_deck) < 1:
            return Statuses.ERR_DECK
        # makes sure the player has the right cards
        needed_cards = [
            ResCard.Wheat,
            ResCard.Ore,
            ResCard.Sheep
        ]
        if not player.has_cards(needed_cards):
            return Statuses.ERR_CARDS
        # removes the cards
        player.remove_cards(needed_cards)
        # gives the player a dev card
        card = self.dev_deck[0]
        player.add_dev_card(card)
        # removes that dev card from the deck
        del self.dev_deck[0]

        if card == DevCard.VictoryPoint:
          self.check_for_win()
        if self.log: self.log.log_player_buys_dev_card(player)

        return Statuses.ALL_GOOD

    # gives players the proper cards for a given roll
    def add_yield_for_roll(self, roll):
        self.board.add_yield(roll)

    # trades cards (given in an array) between two players
    def trade(self, player_one, player_two, cards_one, cards_two):
        # check if they players have the cards they are trading
        # Needs to do this before deleting because one might have the cards while the other does not
        if not player_one.has_cards(cards_one):
            return Statuses.ERR_CARDS

        elif not player_two.has_cards(cards_two):
            return Statuses.ERR_CARDS

        else:
            # removes the cards
            player_one.remove_cards(cards_one)
            player_two.remove_cards(cards_two)
            # add the new cards
            player_one.add_cards(cards_two)
            player_two.add_cards(cards_one)
            return Statuses.ALL_GOOD

    # moves the robber
    # Note that player is the player moving the robber
    # and victim is the player whose card is being taken
    def move_robber(self, tile, player, victim):
        logging.debug("move_robber %s %s %s" % (tile, player, victim))
        # checks the player wants to take a card from somebody
        if victim != None:
            # checks the victim has a settlement on the tile
            has_settlement = False
            # Iterate over points and check if there is a settlement/city on any of them
            #points = self.board.get_connected_points(tile.position[0], tile.position[1])
            points = tile.points
            for p in points:
                if p != None and p.building != None:
                    # Check the victim owns the settlement/city
                    if p.building.owner == victim.get_num():
                        has_settlement = True

            if not has_settlement:
                return Statuses.ERR_INPUT

        # moves the robber
        self.board.move_robber(tile)

        # takes a random card from the victim
        if victim != None:
            # removes a random card from the victim
            if victim.cards:
              card = random.choice(victim.cards)
              victim.remove_cards([card])
              # adds it to the player
              player.add_cards([card])

              if self.log: self.log.log_player_moves_robber_and_steals(player, tile, victim)
        else:
          if self.log: self.log.log_player_moves_robber_and_steals(player, tile, None)
          
        return Statuses.ALL_GOOD

    # trades cards from a player to the bank
    # either by 4 for 1 or using a harbor
    def trade_to_bank(self, player, cards, request):
        # makes sure the player has the cards
        if not player.has_cards(cards):
            return Statuses.ERR_CARDS
        # checks all the cards are the same type
        card_type = cards[0]
        for c in cards[1:]:
            if c != card_type:
                return Statuses.ERR_CARDS
        # if there are not four cards
        if len(cards) != 4:
            # checks if the player has a settlement on the right type of harbor
            has_harbor = False
            harbor_types = player.get_connected_harbor_types()
            print(harbor_types)
            for h_type in harbor_types:
                if Harbor.get_card_from_harbor_type(h_type) == card_type and len(cards) == 2:
                    has_harbor = True
                    break
                elif Harbor.get_card_from_harbor_type(h_type) == None and len(cards) == 3:
                    has_harbor = True
                    break

            if not has_harbor:
                return Statuses.ERR_HARBOR

        # removes cards
        player.remove_cards(cards)
        # adds the new card
        player.add_cards([request])

        ## log trade
        if self.log: self.log.log_player_trades_with_bank(player, cards, request)

        return Statuses.ALL_GOOD

    # gives the longest road to the correct player
    def set_longest_road(self):
        # The length of the current longest road segment
        longest = 0
        owner = self.longest_road_owner

        for p in self.players:
            # longest road needs to be longer than anbody else's
            # and at least 5 road segments long
            if p.longest_road_length > longest and p.longest_road_length >= 5:
                longest = p.longest_road_length
                owner = p

        if self.longest_road_owner != owner:
            self.longest_road_owner = owner
            # checks if the player has won now that they has longest road
            self.check_for_win()

    def check_for_win(self):
      for player in self.players:
        if player.get_VP(include_dev=True) >= self.points_to_win:
          self.has_ended = True
          self.winner = player
          return True
      return False

    # changes a settlement on the board for a city
    def upgrade_settlement(self, point, player):
        status = self.board.upgrade_settlement(player, point)

        if status == Statuses.ALL_GOOD:
            # checks if the player won
            if self.log: self.log.log_player_buys_city(player, point)
            self.check_for_win()

        return status

    # uses a developement card
    # the required args will vary between different dev cards
    def use_dev_card(self, player, card, args):
        # checks the player has the development card
        if not player.has_dev_cards([card]):
            return Statuses.ERR_CARDS

        # applies the action
        if card == DevCard.Road:
            # checks the correct arguments are given
            road_names = [
                "road_one",
                "road_two"
            ]
            for r in road_names:
                if not r in args:
                    return Statuses.ERR_INPUT

                else:
                    # Check the roads have a start and an end
                    if not "start" in args[r] or not "end" in args[r]:
                        return Statuses.ERR_INPUT

            # checks the road location is valid

            # whether the other road is completely isolated but is connected to this road
            other_road_is_isolated = False

            for r in road_names:
                location_status = player.road_location_is_valid(args[r]['start'], args[r]['end'])

                # if the road location is not OK
                # since the player can build two roads, some
                # locations that would be invalid are valid depending on the other road location
                if not location_status == Statuses.ALL_GOOD:
                    # checks if it is isolated, but would be connected to the other road
                    if location_status == Statuses.ERR_ISOLATED:
                        # if the other road is also isolated, just return an error
                        if other_road_is_isolated:
                            return location_status

                        # checks if the two roads are connected
                        # (since the other one is connected, this road is connected through it)
                        road_points = [
                            "start",
                            "end"
                        ]
                        roads_are_connected = False
                        for p_one in road_points:
                            for p_two in road_points:
                                if args["road_one"][p_one] == args['road_two'][p_two]:
                                    other_road_is_isolated = True
                                    # doesn't return an isolated error
                                    roads_are_connected = True

                        if not roads_are_connected:
                            return location_status
                    else:
                        return location_status

            # builds the roads
            for r in road_names:
                self.board.add_road(Road(owner=player.get_num(), point_one=args[r]["start"], point_two=args[r]["end"]))

            self.played_devcard = True
            if self.log: self.log.log_player_plays_road_builder(player, (args[road_names[0]]["start"], args[road_names[0]]["end"]), (args[road_names[1]]["start"], args[road_names[1]]["end"]))


        elif card == DevCard.Knight:
            # checks there are the right arguments
            if not ("robber_tile" in args and "victim" in args):
                logging.error("err input1")
                return Statuses.ERR_INPUT

            # checks the victim input is valid
            if args["victim"] != None:
                if args["victim"] not in self.players or args["victim"] == player:
                    logging.error("err input2")
                    return Statuses.ERR_INPUT

            # moves the robber
            result = self.move_robber(tile=args["robber_tile"], player=player, victim=args["victim"])

            if result != Statuses.ALL_GOOD:
                logging.error("err input3")
                return result

            if self.log: self.log.log_player_plays_knight(player, args["robber_tile"], args["victim"])

            # adds one to the player's knight count
            player.knight_cards += 1

            # checks for the largest army
            if self.largest_army == None:
                # if nobody has the largest army, the player needs at least 3 cards
                if player.knight_cards >= 3:
                    self.largest_army = player

            else:
                # the player needs to have more than anybody else
                current_longest = self.largest_army.knight_cards

                if player.knight_cards > current_longest:
                    self.largest_army = player
            self.played_devcard = True
            self.check_for_win()

        elif card == DevCard.Monopoly:
            # gets the type of card
            card_type = args['card_type']
            # for each player, checks if they have the card
            for p in self.players:
                if p.has_cards([card_type]):
                    # gets how many this player has
                    number_of_cards = p.cards.count(card_type)
                    cards_to_give = [card_type] * number_of_cards
                    # removes the cards
                    p.remove_cards(cards_to_give)
                    # adds them to the user's cards
                    player.add_cards(cards_to_give)
            self.played_devcard = True
            if self.log: self.log.log_player_plays_monopoly(player, args["card_type"])

        elif card == DevCard.VictoryPoint:
            # players do not play developement cards, so it returns an error
            return Statuses.ERR_INPUT

        elif card == DevCard.YearOfPlenty:
            # checks the player gave two development cards
            if not 'card_one' in args and not 'card_two' in args:
                return Statuses.ERR_INPUT

            # gives the player 2 resource cards of their choice
            player.add_cards([
                args['card_one'],
                args['card_two']
            ])

            self.played_devcard = True
            if self.log: self.log.log_player_plays_year_of_plenty(player, args["card_one"], args["card_two"])
        else:
            logging.error("error3")
            return Statuses.ERR_INPUT

        # removes the card
        player.remove_dev_card(card)

        return Statuses.ALL_GOOD

    # simulates 2 dice rolling
    def get_roll(self):
      if self.rolled_dice: 
        raise CatanError(pycatan.Statuses.ERR_INPUT)
      #roll = round(random.random() * 6) + round(random.random() * 6)
      roll = random.randint(1,6) + random.randint(1,6)
      self.rolled_dice = True
      return roll

    def get_point(self, i, j=None):
      if j is None:
        return self.board.points[i[0]][i[1]]
      return self.board.points[i][j]

    def get_tile(self, i, j=None):
      if j is None:
        return self.board.tiles[i[0]][i[1]]
      return self.board.tiles[i][j]

    def start_turn(self, player):
      if self.log: self.log.log_player_start_turn(player)
      self.currentPlayer = player
      self.rolled_dice = False
      self.played_devcard = False

    def finished_turn(self, player):
      player.finished_turn()
      if self.log: self.log.log_player_ends_turn(player)
      self.currentPlayer = None
      pass

    def dict(self):
      d = {}
      d['board'] = self.board
      d['points_to_win'] = self.points_to_win
      d['dev_deck'] = self.dev_deck
      d['players'] = self.players
      return d

    def save(self):
      d = self.dict()
      s = json.dumps(d, sort_keys=True, indent=2, cls=DefaultEncoder)
      return s

    def load(self, fn):
      d = json.loads(open(fn).read())
      self.points_to_win = d['points_to_win']

      self.dev_deck = []
      for card in d['dev_deck']:
        self.dev_deck.append(getattr(DevCard, card))

      for player_data in d['players']:
        player = self.players[player_data['num']]
        player.load(player_data)

      self.board.load(d['board'])
      
class DefaultEncoder(json.JSONEncoder):
  def default(self, o):
    return o.dict()
