#! /usr/bin/env python3

"""python program to solve the world problems..."""

import os, sys, string, time, logging, argparse
import pycatan
import board_renderer
import random

import random_ai

_version = "0.1"

def start():
  g = pycatan.Game()
  g.add_settlement(0, g.get_point(3,5), True)
  g.add_settlement(0, g.get_point(3,2), True)

  roads = g.players[0].get_available_roads()
  br = board_renderer.BoardRenderer(g.board, [50, 10])
  br.render()
  time.sleep(1)

  for (p1, p2) in roads:
    res = g.add_road(0, p1, p2, True)
    br.render()
    time.sleep(1)
    


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
