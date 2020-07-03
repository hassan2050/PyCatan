#! /usr/bin/env python3

"""python program to solve the world problems..."""

import os, sys, string, time, logging, argparse
import pycatan
try:
  import board_renderer
expect ImportError:
  board_renderer = None
import random

import random_ai
import random2_ai

_version = "0.1"

class CatanSim:
  def __init__(self, players):
    self.game = pycatan.Game()
    logging.debug("%s players" % len(self.game.players))
    self.currentPlayer = None
    self.mode = "init"
    
    players = players[:]
    random.shuffle(players)

    for n,player in enumerate(self.game.players):
      player.controller = players[n]
      player.controller.attach(player)
      

  def roll_dice(self, player):
    if self.mode != "preroll": return pycatan.Statuses.ERR_INPUT
    self.mode = "rolled"
    roll = self.game.get_roll()
    logging.debug("rolled %d" % roll)

    if roll == 7:
      ## card check
      for player in self.game.players:
        if len(player.cards) > 7:
          player.controller.remove_cards(len(player.cards) // 2)

      ## move robber
      (tile, victim) = player.controller.move_robber(self)
      logging.debug("%s: move_robber: tile:%s victim:%s" % (player, tile, victim))
      rc = self.game.move_robber(tile, player, victim)
      assert rc == pycatan.Statuses.ALL_GOOD
    else:
      ## produce goods
      self.game.add_yield_for_roll(roll)

    return pycatan.Statuses.ALL_GOOD

  def start(self, br):
    br.board = self.game.board

    self.mode = "choose starting"
    for player in self.game.players:
      self.currentPlayer = player
      player.controller.choose_starting_settlement()
    for player in reversed(self.game.players):
      self.currentPlayer = player
      player.controller.choose_starting_settlement()

    #br.render()
    #time.sleep(1)

    round = 0
    while not self.game.has_ended:
      round += 1
      scores = [p.get_VP(include_dev=True) for p in self.game.players]

      logging.debug("Round %d: %s" % (round, scores))

      for player in self.game.players:
        self.mode = "preroll"
        self.currentPlayer = player
        player.controller.take_turn(self)
        
        if self.game.has_ended: break

        #br.render()
        #time.sleep(1)

    self.mode = "finished"
    #br.render()
    #time.sleep(.1)
    scores = [p.get_VP(include_dev=True) for p in self.game.players]
    logging.info("Round %d: %s" % (round, scores))

    for p in self.game.players:
      if p.get_VP(include_dev=True) >= self.game.points_to_win:
        p.controller.win+=1
      else:
        p.controller.lose+=1

    
    

def start():
  if board_renderer:
    br = board_renderer.BoardRenderer(None, [60, 10])
    br.clear()

  players = []
  players.append(random_ai.RandomPlayer("random1a"))
  players.append(random_ai.RandomPlayer("random1b"))
  players.append(random2_ai.Random2Player("random2"))

  ngames = 0
  while 1:
    c = CatanSim(players)
    c.start(br)
    ngames += 1 

    stats = []
    stats.append("%s" % ngames)
    for p in players:
      stats.append("%s: %.1f" % (p.name, 100.*p.win / (p.win+p.lose)))
    logging.info(stats)
  
def test():
  logging.warn("Testing")

def parse_args(argv):
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=__doc__)

  parser.add_argument("-t", "--test", dest="test_flag", 
                    default=False,
                    action="store_true",
                    help="Run test function")
  parser.add_argument("--log-level", type=str,
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Desired console log level")
  parser.add_argument("-d", "--debug", dest="log_level", action="store_const",
                      const="DEBUG",
                      help="Activate debugging")
  parser.add_argument("-i", "--info", dest="log_level", action="store_const",
                      const="INFO",
                      help="Activate info")
  parser.add_argument("-q", "--quiet", dest="log_level", action="store_const",
                      const="CRITICAL",
                      help="Quite mode")
  #parser.add_argument("files", type=str, nargs='+')

  args = parser.parse_args(argv[1:])
  if args.log_level is None: args.log_level = "INFO"

  return parser, args

def main(argv, stdout, environ):
  if sys.version_info < (3, 0): reload(sys); sys.setdefaultencoding('utf8')

  parser, args = parse_args(argv)

  numeric_loglevel = getattr(logging, args.log_level.upper(), None)
  if not isinstance(numeric_loglevel, int):
    raise ValueError('Invalid log level: %s' % args.log_level)

  logging.basicConfig(format="[%(asctime)s] %(levelname)-8s %(message)s", 
                    datefmt="%m/%d %H:%M:%S", level=numeric_loglevel)

  if args.test_flag:  test();   return
  
  start()

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
