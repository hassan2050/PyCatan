"""
module catanlog provides a reference implementation for the catanlog (.catan) file format.

See class CatanLog for documentation.
"""
import copy
import datetime
import os
import sys
import json

__version__ = '0.9.3'

class DefaultEncoder(json.JSONEncoder):
  def default(self, o):
    return o.dict()

class CatanLog(object):
    """
    class CatanLog introduces a machine-parsable, human-readable log of all actions made in a game of Catan.

    Each log contains all publicly known information in the game.
    Each log is sufficient to 'replay' a game from a spectator's point of view.

    This logger is for raw game actions only. No derivable or inferrable information will be logged.
    - e.g. players discarding cards on a 7 is not logged, because it is derivable from previous
           rolls, purchases, etc.

    The files are explicitly versioned by the class variable version, and versioning follows semver.

    Use #dump to get the log as a string.
    Use #flush to write the log to a file.

    TODO maybe log private information as well (which dev card picked up, which card stolen)
    """
    sequence = 0

    def __init__(self, auto_flush=True, log_dir='log', use_stdout=False):
        """
        Create a CatanLog object using the given options. The defaults are fine.

        :param auto_flush: flush the log to file after every log() call, bool
        :param log_dir: directory to write the log to, str
        :param use_stdout: if True, flush() will write to stdout instead of to file
        """
        CatanLog.sequence += 1
        self._log_dir = log_dir
        self._history = []
        self._log = {}
        self._log['history'] = self._history

        self._game_start_timestamp = datetime.datetime.now()
        self._latest_timestamp = copy.deepcopy(self._game_start_timestamp)

    def logpath(self):
        """
        Return the logfile path and filename as a string.

        The file with name self.logpath() is written to on flush().

        The filename contains the log's timestamp and the names of players in the game.
        The logpath changes when reset() or _set_players() are called, as they change the
        timestamp and the players, respectively.
        """
        name = '{}-{}.catan'.format(self.timestamp_str(), CatanLog.sequence)
        path = os.path.join(self._log_dir, name)
        if not os.path.exists(self._log_dir):
            os.mkdir(self._log_dir)
        return path

    def timestamp_str(self):
        #return self._game_start_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return self._game_start_timestamp.strftime('%Y%m%d-%H%M%S')

    def save(self):
      s = json.dumps(self._log, sort_keys=True, indent=2, cls=DefaultEncoder)
      open(self.logpath(), "w").write(s)

    def log_game_start(self, game):
        """
        Begin a game.

        Erase the log, set the timestamp, set the players, and write the log header.

        The robber is assumed to start on the desert (or off-board).

        :param players: iterable of catan.game.Player objects
        :param terrain: list of 19 catan.board.Terrain objects.
        :param numbers: list of 19 catan.board.HexNumber objects.
        :param ports: list of catan.board.Port objects.
        """
        self._log = game.dict()
        self._log['version'] = __version__
        self._log['timestamp'] = self.timestamp_str()
        self._log['history'] = self._history

    def log_player_roll(self, player, roll):
        """
        :param player: catan.game.Player
        :param roll: integer or string, the sum of the dice
        """
        self._turn.append(("roll", roll))

    def log_player_moves_robber_and_steals(self, player, location, victim):
        """
        :param player: catan.game.Player
        :param location: string, see hexgrid.location()
        :param victim: catan.game.Player
        """
        if victim is None:
          self._turn.append(['move_robber', location.position])
        else:
          self._turn.append(['move_robber_and_steals', location.position, victim.color])

    def log_player_buys_road(self, player, start, end):
        """
        :param player: catan.game.Player
        :param location: string, see hexgrid.location()
        """
        self._turn.append(['build_road', start, end])

    def log_player_buys_settlement(self, player, location):
        """
        :param player: catan.game.Player
        :param location: string, see hexgrid.location()
        """
        self._turn.append(['build_settlement', location])

    def log_player_buys_city(self, player, location):
        """
        :param player: catan.game.Player
        :param location: string, see hexgrid.location()
        """
        self._turn.append(['build_city', location])

    def log_player_buys_dev_card(self, player):
        """
        :param player: catan.game.Player
        """
        self._turn.append(['build_devcard'])


    def log_player_trades_with_bank(self, player, to_bank, to_player):
        self._turn.append(['trade_bank', to_bank, to_player])

    def log_player_trades_with_port(self, player, to_port, port, to_player):
        """
        :param player: catan.game.Player
        :param to_port: list of tuples, [(int, game.board.Terrain), (int, game.board.Terrain)]
        :param port: catan.board.Port
        :param to_player: list of tuples, [(int, game.board.Terrain), (int, game.board.Terrain)]
        """
        self._turn.append(['trade_port', to_port, port, to_player])

    def log_player_trades_with_other_player(self, player, to_other, other, to_player):
        """
        :param player: catan.game.Player
        :param to_other: list of tuples, [(int, game.board.Terrain), (int, game.board.Terrain)]
        :param other: catan.board.Player
        :param to_player: list of tuples, [(int, game.board.Terrain), (int, game.board.Terrain)]
        """
        self._turn.append(['trade_player',  to_other, other.color, to_player])

    def log_player_plays_knight(self, player, location, victim):
        """
        :param player: catan.game.Player
        :param location: string, see hexgrid.location()
        :param victim: catan.game.Player
        """
        if victim:
          self._turn.append(['play_knight', location.position, victim.color])
        else:
          self._turn.append(['play_knight', location.position])

    def log_player_plays_road_builder(self, player, location1, location2):
        """
        :param player: catan.game.Player
        :param location1: string, see hexgrid.location()
        :param location2: string, see hexgrid.location()
        """
        self._turn.append(['play_road_builder', location1, location2])

    def log_player_plays_year_of_plenty(self, player, resource1, resource2):
        """
        :param player: catan.game.Player
        :param resource1: catan.board.Terrain
        :param resource2: catan.board.Terrain
        """
        self._turn.append(['play_year_of_plenty', resource1, resource2])

    def log_player_plays_monopoly(self, player, resource):
        """
        :param player: catan.game.Player
        :param resource: catan.board.Terrain
        """
        self._turn.append(['play_monopoly', resource])

    def log_player_plays_victory_point(self, player):
        """
        :param player: catan.game.Player
        """
        self._turn.append(["victorypoint"])

    def log_player_start_turn(self, player):
      self._turn = []
      self._history.append([player.color, self._turn])

    def log_player_ends_turn(self, player):
        """
        :param player: catan.game.Player
        """
        seconds_delta = (datetime.datetime.now() - self._latest_timestamp).total_seconds()
        #self._history.append(["endturn", player.color, round(seconds_delta)])
        self.turn = []
        self._latest_timestamp = datetime.datetime.now()

    def log_player_wins(self, player):
        """
        :param player: catan.game.Player
        """
        self._history.append(["wins", player.color])

