#! /usr/bin/env python3

"""python program to solve the world problems..."""

import os, sys, string, time, logging, argparse
import random
import pycatan
from pycatan import ResCard, DevCard, Statuses

class AIPlayer:
  def __init__(self, game, player):
    self.game = game
    self.player = player

  def choose_starting_settlement(self):
    logging.debug("P%s: choose" % self.player.num)

    bpoints = [item for sublist in self.game.board.points for item in sublist]
    random.shuffle(bpoints)

    for p in bpoints:
      if p.building: continue

      r = self.game.add_settlement(self.player.num, p, is_starting=True)
      if r == pycatan.Statuses.ALL_GOOD: 
        cpoints = p.connected_points[:]
        random.shuffle(cpoints)
        for p2 in cpoints:
          r = self.game.add_road(self.player.num, p, p2, is_starting=True)
          if r == pycatan.Statuses.ALL_GOOD: 
            return

  def take_turn(self, sim):
    logging.debug("P%s: take_turn" % self.player.num)

    logging.debug("P%s: %s" % (self.player.num, self.player.cards))

    sim.roll_dice(self.player)

    error_actions = []

    while 1:
      actions = []
      if self.player.has_cards([ResCard.Wood, ResCard.Brick]):
        ## check if there are any available spots
        available_roads = self.player.get_available_roads()
        if available_roads and self.player.num_roads > 0:
          actions.append(("build_road", available_roads))

      if self.player.has_cards([ResCard.Wood, ResCard.Brick, ResCard.Wheat, ResCard.Sheep]):
        ## check if there are any available spots
        available_points = self.player.get_available_settlements()
        if available_points and self.player.num_settlements > 0:
          actions.append(("build_settlement", available_points))

      if self.player.has_cards([ResCard.Ore, ResCard.Wheat, ResCard.Sheep]):
        if len(self.game.dev_deck) > 0:
          actions.append(("build_dev", None))

      if len(self.player.cards) > 0:
        cards = []
        for ctype in (ResCard.Wood, ResCard.Brick, ResCard.Wheat, ResCard.Sheep, ResCard.Ore):
          n = self.player.cards.count(ctype)
          if n >= 4:
            cards.append(ctype)
        if cards:
          actions.append(("trade_to_bank", cards))

      if self.player.has_cards([ResCard.Ore, ResCard.Ore, ResCard.Ore, ResCard.Wheat, ResCard.Wheat]):
        bpoints = [item for sublist in self.game.board.points for item in sublist]
        settlements = []
        for p in bpoints:
          if p.building and p.building.owner == self.player.num and p.building.type == pycatan.Building.BUILDING_SETTLEMENT:
            settlements.append(p)
        if settlements and self.player.num_cities > 0:
          actions.append(("upgrade_settlement", settlements))

      if self.player.dev_cards:
        playable = []
        logging.debug ("dev_cards: %s" % self.player.dev_cards)
        for c in self.player.dev_cards:
          if c == DevCard.VictoryPoint: continue
          if c == DevCard.Road: continue
          if c == DevCard.Road:
            if self.player.num_roads >= 2:
              available_roads = self.player.get_available_roads()
              if len(available_roads) >= 2:
                playable.append(c)
          else:
            playable.append(c)
        if playable:
          actions.append(("use_dev_card", playable))

      ## remove the actions that caused errors
      actions = [(action,args) for action,args in actions if action not in error_actions]
      if len(actions) == 0: break

      logging.debug("P%s: actions %s" % (self.player.num, actions))

      action = random.choice(actions)
      cmd = action[0]

      if cmd == "build_road":
        available_roads = action[1]
        (p1, p2) = random.choice(available_roads)
        logging.debug("P%s: build_road %s %s" % (self.player.num, p1, p2))

        res = self.game.add_road(self.player.num, p1, p2)
        if res != Statuses.ALL_GOOD: 
          logging.error("P%s: build_road %s" % (self.player.num, res))
          error_actions.append("build_road")

      elif cmd == "build_settlement":
        available_points = action[1]
        point = random.choice(available_points)
        logging.debug("P%s: build_settlement %s" % (self.player.num, point))
        res = self.game.add_settlement(self.player.num, point)
        if res != Statuses.ALL_GOOD: 
          logging.error("add_settlement %s" % res)
          error_actions.append("add_settlement")
        assert res == Statuses.ALL_GOOD

      elif cmd == "upgrade_settlement":
        available_points = action[1]
        point = random.choice(available_points)
        logging.debug("P%s: upgrade_settlement %s" % (self.player.num, point))
        res = self.game.add_city(point, self.player.num)
        if res != Statuses.ALL_GOOD: 
          logging.error("P%s: upgrade_settlement %s" % (self.player.num, res))
          error_actions.append("upgrade_settlement")
        assert res == Statuses.ALL_GOOD

      elif cmd == "build_dev":
        logging.debug("build_dev")
        res = self.game.build_dev(self.player.num)
        if res != Statuses.ALL_GOOD: 
          logging.error("P%s: build_dev %s" % (self.player.num, res))
          error_actions.append("build_dev")
      elif cmd == "use_dev_card":
        available_cards = action[1]
        card = random.choice(available_cards)
        args = {}
        if card == DevCard.YearOfPlenty:
          args['card_one'] = random.choice([ResCard.Wood, ResCard.Brick, ResCard.Ore, ResCard.Sheep, ResCard.Wheat])
          args['card_two'] = random.choice([ResCard.Wood, ResCard.Brick, ResCard.Ore, ResCard.Sheep, ResCard.Wheat])
        elif card == DevCard.Knight:
          (tile, victim) = self.move_robber(sim)
          args['robber_pos'] = tile
          args['victim'] = victim
        elif card == DevCard.Monopoly:
          args['card_type'] = random.choice([ResCard.Wood, ResCard.Brick, ResCard.Ore, ResCard.Sheep, ResCard.Wheat])
        elif card == DevCard.Road:
          available_roads = self.player.get_available_roads()
          (p1, p2) = random.choice(available_roads)
          available_roads.remove((p1,p2))
          args['road_one'] = {"start":p1, "end":p2}
          (p1, p2) = random.choice(available_roads)
          args['road_two'] = {"start":p1, "end":p2}
        res = self.game.use_dev_card(self.player.num, card, args)
        if res != Statuses.ALL_GOOD: 
          logging.error("P%s: use_dev_card %s %s %s" % (self.player.num, res.name, card.name, args))
          error_actions.append("use_dev_card")
        
      elif cmd == "trade_to_bank":
        card = random.choice(action[1])
        possble_cards = [ResCard.Wood, ResCard.Brick, ResCard.Ore, ResCard.Sheep, ResCard.Wheat]
        possble_cards.remove(card)
        request = random.choice(possble_cards)
        res = self.game.trade_to_bank(self.player.num, [card]*4, request)
        if res != Statuses.ALL_GOOD: 
          logging.error("P%s: trade_to_bank %s %s %s" % (self.player.num, res, card, request))
          error_actions.append("trade_to_bank")

  def remove_cards(self, ncards):
    for i in range(ncards):
      j = random.choice(range(len(self.player.cards)))
      c = self.player.cards[j]
      del self.player.cards[j]
      logging.debug("P%s: discarded %s" % (self.player.num, c))

  def move_robber(self, sim):
    logging.debug("P%s: move_robber" % self.player.num)

    tiles = [item for sublist in self.game.board.tiles for item in sublist]
    tile = random.choice(tiles)
    
    potential = []
    for p in tile.points:
      if p.building and p.building.owner != self.player.num:
        potential.append(p.building.owner)

    victim = None
    if potential:
      victim = random.choice(potential)

    return (tile, victim)

    
