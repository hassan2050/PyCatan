from pycatan.board import Board
from pycatan.game import Game
from pycatan.statuses import Statuses
from pycatan.card import ResCard
from pycatan.tile_type import TileType
from pycatan.tile import Tile

import random

class TestBoard:
    def test_card_to_tile_conversion(self):
        # Check that the board switches between tile types and the corresponding card properly
        assert Board.get_card_from_tile(TileType.Forest), ResCard.Wood
    def test_give_proper_yield(self):
        # Set seeed to ensure the board is the same as the testcase
        random.seed(1)
        # Create new game and get the board
        game = Game()
        board = game.board
        player0 = game.players[0]
        # Make sure robber is not on the top-left tile
        board.robber = [1, 1]
        # add settlement
        game.add_settlement(player0, game.get_point(0,0), True)
        # give the roll
        board.add_yield(8)
        # check the board gave the cards correctly
        assert player0.has_cards([ResCard.Brick])

    def test_robber_prevents_yield(self):
        random.seed(1)
        game = Game()
        board = game.board
        player0 = game.players[0]
        # Move robber to top-left corner
        board.robber = game.get_tile(0,0)
        # Add settlement
        game.add_settlement(player0, game.get_point(0,0), True)
        # Roll an 8
        board.add_yield(8)
        # Ensure the robber prevented the player from getting the card
        assert not player0.has_cards([ResCard.Brick])

