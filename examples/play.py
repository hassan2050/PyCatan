#! /usr/bin/env python3

"""python program to solve the world problems..."""

import os, sys, string, time, logging, argparse
import pycatan
import board_renderer
import random

import random_ai

_version = "0.1"

class CatanSim:
  def __init__(self):
    self.game = pycatan.Game()
    logging.debug("%s players" % len(self.game.players))

    for player in self.game.players:
      player.controller = random_ai.AIPlayer(self.game, player)
    
  def roll_dice(self, player):
    roll = self.game.get_roll()
    logging.debug("rolled %d" % roll)

    if roll == 7:
      ## card check
      for player in self.game.players:
        if len(player.cards) > 7:
          player.controller.remove_cards(len(player.cards) // 2)

      ## move robber
      (tile, victim) = player.controller.move_robber(self)
      logging.debug("P%s: move_robber: tile:%s victim:%s" % (player.num, tile, victim))
      self.game.move_robber(tile, player.num, victim)
    else:
      ## produce goods
      self.game.add_yield_for_roll(roll)

  def start(self):
    for player in self.game.players:
      player.controller.choose_starting_settlement()
    for player in reversed(self.game.players):
      player.controller.choose_starting_settlement()

    br = board_renderer.BoardRenderer(self.game.board, [50, 10])
    #br.render()
    #time.sleep(1)

    round = 0
    while not self.game.has_ended:
      round += 1
      scores = [p.get_VP(include_dev=True) for p in self.game.players]

      logging.debug("Round %d: %s" % (round, scores))

      for player in self.game.players:
        player.controller.take_turn(self)
        
        if self.game.has_ended: break

        #br.render()
        #time.sleep(1)

    br.render()
    #time.sleep(.1)
    scores = [p.get_VP(include_dev=True) for p in self.game.players]
    logging.info("Round %d: %s" % (round, scores))
    

def start():
  while 1:
    c = CatanSim()
    c.start()
  
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
  parser.add_argument("-q", "--quiet", dest="log_level", action="store_const",
                      const="CRITICAL",
                      help="Quite mode")
  #parser.add_argument("files", type=str, nargs='+')

  args = parser.parse_args(argv[1:])
  if args.log_level is None: args.log_level = "WARN"

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
