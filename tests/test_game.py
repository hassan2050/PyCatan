from pycatan.game import Game
from pycatan.building import *
from pycatan.card import ResCard
from pycatan.statuses import Statuses
from pycatan.harbor import HarborType
import random
import logging

class TestGame:

    def test_game_uses_three_players_by_default(self):
        game = Game()
        assert len(game.players) == 3
    def test_game_starts_with_variable_players(self):
        game = Game(num_of_players=5)
        assert len(game.players) == 5
    def test_adding_starting_settlements(self):
        # Create game
        g = Game();
        player0 = g.players[0]
        player1 = g.players[1]
        player2 = g.players[2]
        # Make sure creating a starting settlement does not use any cards
        g.players[0].add_cards([
            ResCard.Wood,
            ResCard.Brick,
            ResCard.Sheep,
            ResCard.Wheat
        ])
        # Test adding a starting settlement, i.e. no cards needed
        res = g.add_settlement(player0, g.get_point(0,0), True)
        assert res == Statuses.ALL_GOOD
        assert g.get_point(0,0).building != None
        assert g.get_point(0,0).building.type == BuildingType.Settlement
        assert g.get_point(0,0).building.point is g.board.points[0][0]
        assert len(player0.cards) == 4
        # Test adding a settlement too close to another settlement
        res = g.add_settlement(player1, g.get_point(0,1), True)
        assert res == Statuses.ERR_BLOCKED
        # Test adding a settlement the correct distance away
        res = g.add_settlement(player2, g.get_point(0,2), True)
        assert res == Statuses.ALL_GOOD
    def test_adding_starting_roads(self):
        # Create game
        g = Game()
        player0 = g.players[0]
        player1 = g.players[1]
        player2 = g.players[2]
        # Add starting settlement
        g.add_settlement(player0, g.get_point(0,0), True)
        # Try adding a road
        res = g.add_road(player0, g.get_point(0,0), g.get_point(0,1), True)
        assert res == Statuses.ALL_GOOD
        res = g.add_road(player0, g.get_point(1,1), g.get_point(0,0), True)
        assert res == Statuses.ALL_GOOD
        # Try adding a disconnected road
        res = g.add_road(player0, g.get_point(2,0), g.get_point(2,1), True)
        assert res == Statuses.ERR_ISOLATED
        # Try adding a road whose point's are not connected
        res = g.add_road(player0, g.get_point(0,0), g.get_point(5,5), True)
        assert res == Statuses.ERR_NOT_CON
        # Try adding a road connected to another player's settlement
        g.add_settlement(player1, g.get_point(2,2), True)
        res = g.add_road(player0, g.get_point(2,2), g.get_point(2,3), True)
        assert res == Statuses.ERR_ISOLATED
    # Test that player.add_settlement returns the proper value
    def test_add_settlement(self):
        g = Game()
        player0 = g.players[0]
        player1 = g.players[1]
        player2 = g.players[2]
        # Try to add a settlement without the cards
        g.add_settlement(player0, g.get_point(0,0))
        # Add cards to build a settlement
        player0.add_cards([
            ResCard.Wood,
            ResCard.Brick,
            ResCard.Sheep,
            ResCard.Wheat
        ])
        # Try adding an isolated settlement
        res = g.add_settlement(player0, g.get_point(0,0))
        assert res == Statuses.ERR_ISOLATED
        assert g.get_point(0,0).building == None
        # Add starting settlement and two roads to ensure there is an available position
        assert g.add_settlement(player0, g.get_point(0,2), True) == Statuses.ALL_GOOD
        assert g.add_road(player0, g.get_point(0,2), g.get_point(0,1), True) == Statuses.ALL_GOOD
        assert g.add_road(player0, g.get_point(0,0), g.get_point(0,1), True) == Statuses.ALL_GOOD
        res = g.add_settlement(player0, g.get_point(0,0))
        assert res == Statuses.ALL_GOOD
        assert g.get_point(0,0).building != None
        assert g.get_point(0,0).building.type == BuildingType.Settlement
    # Test trading in cards either directly through the bank
    def test_trade_in_cards_through_bank(self):
        g = Game()
        player0 = g.players[0]
        player1 = g.players[1]
        player2 = g.players[2]
        # Add 4 wood cards to player 0
        player0.add_cards([ResCard.Wood] * 4)
        # Try to trade in for 1 wheat
        res = g.trade_to_bank(player0, cards=[ResCard.Wood] * 4, request=ResCard.Wheat)
        assert res == Statuses.ALL_GOOD
        assert not player0.has_cards([ResCard.Wood])
        assert player0.has_cards([ResCard.Wheat])
        # Try to trade in cards the player doesn't have
        res = g.trade_to_bank(player0, cards=[ResCard.Brick] * 4, request=ResCard.Ore)
        assert res == Statuses.ERR_CARDS
        assert not player0.has_cards([ResCard.Ore])
        # Try to trade in with less than 4 cards, but more than 0
        player0.add_cards([ResCard.Brick] * 3)
        res = g.trade_to_bank(player0, cards=[ResCard.Brick] * 4, request=ResCard.Sheep)
        assert res == Statuses.ERR_CARDS
        assert player0.has_cards([ResCard.Brick] * 3)
        assert not player0.has_cards([ResCard.Sheep])
    def test_trade_in_cards_through_harbor(self):
        g = Game();
        player0 = g.players[0]
        player1 = g.players[1]
        player2 = g.players[2]
        # Add Settlement next to the harbor on the top
        res = g.add_settlement(player0, g.get_point(0,2), is_starting=True)
        assert res == Statuses.ALL_GOOD
        # Make the harbor trade in ore for testing
        for h in g.board.harbors:
            if g.get_point(0,2) in h.get_points():
                h.type = HarborType.Ore
                print("found harbor lmao")
        player0.add_cards([ResCard.Ore] * 2)
        # Try to use harbor
        res = g.trade_to_bank(player0, cards=[ResCard.Ore] * 2, request=ResCard.Wheat)
        assert res == Statuses.ALL_GOOD
        assert player0.has_cards([ResCard.Wheat])
        assert not player0.has_cards([ResCard.Ore])
        # Try to trade in to a harbor that the player does not have access to
        player0.add_cards([ResCard.Brick] * 2)
        res = g.trade_to_bank(player0, cards=[ResCard.Brick] * 2, request=ResCard.Sheep)
        assert res == Statuses.ERR_HARBOR
        assert player0.has_cards([ResCard.Brick] * 2)
        assert not player0.has_cards([ResCard.Sheep])
        # Try to trade without the proper cards
        assert not player0.has_cards([ResCard.Ore])
        res = g.trade_to_bank(player0, cards=[ResCard.Ore] * 2, request=ResCard.Sheep)
        assert res == Statuses.ERR_CARDS
        assert not player0.has_cards([ResCard.Sheep])
        # Try to trade with more cards than the player has
        player0.add_cards([ResCard.Ore])
        res = g.trade_to_bank(player0, cards=[ResCard.Ore] * 2, request=ResCard.Sheep)
        assert res == Statuses.ERR_CARDS
        assert not player0.has_cards([ResCard.Sheep])
        assert player0.has_cards([ResCard.Ore])
    def test_moving_robber(self):
        random.seed(1)
        g = Game()
        player0 = g.players[0]
        player1 = g.players[1]
        player2 = g.players[2]
        # Move the robber
        g.move_robber(g.get_tile(0,0), None, None)
        assert g.board.robber is g.get_tile(0,0)
        # Build a settlement at 1, 1
        g.add_settlement(player0, point=g.get_point(1,1), is_starting=True)
        # Roll an 8
        g.add_yield_for_roll(8)
        # Ensure the player got nothing since the robber was there
        assert len(player0.cards) == 0
        # Give the player a brick to steal
        player0.add_cards([ResCard.Brick])
        # Move the robber to 1, 0 and steal the brick
        g.move_robber(g.get_tile(1,0), player1, player0)
        print(player0.cards, player1.cards)
        # Make sure they stole the brick
        assert player1.has_cards([ResCard.Brick])

    def test_get_buildings(self):
        # Create game
        g = Game()
        player0 = g.players[0]

        buildings = player0.get_buildings()
        assert len(buildings) == 0

        res = g.add_settlement(player0, g.get_point(5,3), True)
        assert res == Statuses.ALL_GOOD

        buildings = player0.get_buildings()
        assert len(buildings) == 1
        
        res = g.add_settlement(player0, g.get_point(3,2), True)
        assert res == Statuses.ALL_GOOD

        buildings = player0.get_buildings()
        assert len(buildings) == 2
        

    def test_get_available_settlements1(self):
        # Create game
        g = Game()
        player0 = g.players[0]

        points = player0.get_available_settlements()
        assert len(points) == 54

    def test_get_available_settlements2(self):
        # Create game
        g = Game()
        player0 = g.players[0]

        res = g.add_settlement(player0, g.get_point(5,3), True)
        assert res == Statuses.ALL_GOOD
        res = g.add_settlement(player0, g.get_point(3,2), True)
        assert res == Statuses.ALL_GOOD

        points = player0.get_available_settlements()
        assert len(points) == 0

    def test_get_available_settlements3(self):
        # Create game
        g = Game()
        player0 = g.players[0]
        res = g.add_settlement(player0, g.get_point(3,5), True)
        assert res == Statuses.ALL_GOOD

        res = g.add_settlement(player0, g.get_point(5,2), True)
        assert res == Statuses.ALL_GOOD

        roads = player0.get_available_roads()
        assert len(roads) == 6
        res = g.add_road(player0, g.get_point(3,5), g.get_point(3,4), True)
        assert res == Statuses.ALL_GOOD

        res = g.add_road(player0, g.get_point(3,4), g.get_point(2,4), True)
        assert res == Statuses.ALL_GOOD

        points = player0.get_available_settlements()
        assert len(points) == 1

    def test_get_available_roads1(self):
        g = Game()
        player0 = g.players[0]

        res = g.add_settlement(player0, g.get_point(0,0), True)
        assert res == Statuses.ALL_GOOD
        res = g.add_road(player0, g.get_point(0,0), g.get_point(0,1), True)
        assert res == Statuses.ALL_GOOD

        roads = player0.get_available_roads()
        logging.info("ROADS %s" % roads)

        assert len(roads) == 2

    def test_get_available_roads2(self):
        g = Game()
        player0 = g.players[0]
        res = g.add_settlement(player0, g.get_point(3,5), True)
        assert res == Statuses.ALL_GOOD
        res = g.add_settlement(player0, g.get_point(3,2), True)
        assert res == Statuses.ALL_GOOD
        roads = player0.get_available_roads()
        logging.info("ROADS %s" % roads)
        assert len(roads) == 6

    def test_get_available_roads3(self):
        g = Game()
        player0 = g.players[0]

        res = g.add_settlement(player0, g.get_point(0,0), True)
        assert res == Statuses.ALL_GOOD
        res = g.add_road(player0, g.get_point(0,0), g.get_point(0,1), True)
        assert res == Statuses.ALL_GOOD

        res = g.add_settlement(player0, g.get_point(3,5), True)
        assert res == Statuses.ALL_GOOD

        roads = player0.get_available_roads()
        logging.info("ROADS %s" % roads)

        assert len(roads) == 5


    def test_upgrade_settlement(self):
        g = Game()
        player0 = g.players[0]
        player1 = g.players[1]

        res = g.add_settlement(player0, g.get_point(5,3), True)
        assert res == Statuses.ALL_GOOD

        buildings = player0.get_buildings()
        assert len(buildings) == 1

        assert buildings[0].type == BuildingType.Settlement

        res = g.upgrade_settlement(buildings[0].point, player0)
        assert res == Statuses.ERR_CARDS

        player0.add_cards([
            ResCard.Wheat,
            ResCard.Wheat,
            ResCard.Ore,
            ResCard.Ore,
            ResCard.Ore
        ])

        res = g.upgrade_settlement(buildings[0].point, player1)
        assert res == Statuses.ERR_BAD_OWNER

        res = g.upgrade_settlement(buildings[0].point, player0)
        assert res == Statuses.ALL_GOOD

        buildings = player0.get_buildings()
        assert len(buildings) == 1

        assert buildings[0].type == BuildingType.City
