#! /usr/bin/env python3

"""python program to solve the world problems..."""

import os, sys, string, time, logging, argparse
import random
import pycatan
from pycatan import ResCard, DevCard, Statuses

import ai_player

class AIPlayer:
  def __init__(self, name):
    self.name = name
    self.game = None
    self.player = None

    self.win = 0
    self.lose = 0

  def attach(self, player):
    self.player = player
    self.game = player.game
    self.player.name = self.name

  def choose_starting_settlement(self):
    pass

  def take_turn(self, sim):
    pass

  def remove_cards(self, ncards):
    pass

  def move_robber(self, sim):
    pass
    
