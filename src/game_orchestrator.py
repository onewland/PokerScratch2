import datetime
import logging
import random
from copy import copy
from enum import Enum
from typing import NamedTuple

from player import Player

GamePhase = Enum('GamePhase',
                 ['NOT_STARTED',
                  'ANTE_PAID',
                  'WAITING_ON_BET',
                  'DEALING_CARD_1',
                  'CARD_1_DEALT',
                  'DEALING_CARD_2',
                  'CARD_2_DEALT',
                  'DEALING_FLOP',
                  'DEALING_TURN',
                  'DEALING_RIVER',
                  'ONE_MAN_REMAINING',
                  'RESOLVE_HANDS_FORCEFULLY'])


class NotEnoughMoneyToContinue(BaseException):
    pass


PHASE_THRESHOLD = 1

class Bet(NamedTuple):
    amount: int
    player: Player

class HoldemGameLoop:
    def __init__(self, game, *, little_ante, big_ante):
        self.game = game
        self.pot = 0
        self.little_ante = little_ante
        self.big_ante = big_ante
        self.game_state: GamePhase = GamePhase.NOT_STARTED
        self.dealer_count = 0
        self.round_players = copy(self.game.players)
        self.game_size = len(self.game.players)
        self.round_size = len(self.game.players)
        self.deck = game.deck
        self.bettor_index = 0
        self.last_raise_player = None
        self.phase_started_at = datetime.datetime.now()
        self.bets = []
        self.current_wager = 0
        self.shared_cards = []
        self.this_round_bets = []

    def __repr__(self):
        return f"state = {self.game_state}\n" + \
               f'pot = {self.pot}\n' + \
               f"current_wager = {self.current_wager}\n" + \
               f"current_bettor = {self.round_players[self.bettor_index]}\n" + \
               f"shared_cards = {self.shared_cards}"

    def advance_if_possible(self):
        if datetime.datetime.now() - self.phase_started_at > datetime.timedelta(seconds=PHASE_THRESHOLD):
            print("Infinite loop probably")
            return False

        # for now, ignoring pre-deal betting
        if self.game_state == GamePhase.NOT_STARTED:
            self.collect_antes_from_players()
            return True

        if self.game_state == GamePhase.ANTE_PAID:
            self.deal_players_two_cards()
            return True

        if self.game_state == GamePhase.WAITING_ON_BET:
            if self.round_size == 1:
                self.advance_phase(GamePhase.ONE_MAN_REMAINING)
            elif self.round_players[self.bettor_index] == self.last_raise_player:
                self.reset_bets()

                if len(self.shared_cards) == 0:
                    self.advance_phase(GamePhase.DEALING_FLOP)
                if len(self.shared_cards) == 3:
                    self.advance_phase(GamePhase.DEALING_TURN)
                if len(self.shared_cards) == 4:
                    self.advance_phase(GamePhase.DEALING_RIVER)
                if len(self.shared_cards) == 5:
                    self.advance_phase(GamePhase.RESOLVE_HANDS_FORCEFULLY)
                return True
            else:
                self.solicit_next_bet()
                return True

        if self.game_state == GamePhase.DEALING_FLOP:
            self.reset_bets()
            # burn and turn?
            self.deck.draw(1)
            self.shared_cards.extend(self.deck.draw(3))
            self.advance_phase(GamePhase.WAITING_ON_BET)
            return True

        if self.game_state == GamePhase.DEALING_FLOP or self.game_state == GamePhase.DEALING_RIVER:
            self.reset_bets()
            # burn and turn?
            self.deck.draw(1)
            self.shared_cards.extend(self.deck.draw(3))
            self.advance_phase(GamePhase.WAITING_ON_BET)
            return True

        if self.game_state == GamePhase.ONE_MAN_REMAINING:
            print(f"awarding pot {self.pot}")
            self.award_pot(self.round_players[0])
            print(f"winner is {self.round_players}")
            standings = "\n".join([str(player) for player in self.game.players])
            print(f"standings = {standings}")

            return False

        else:
            return False

    def collect_antes_from_players(self):
        next_two_player_indices = [(self.dealer_count + 1) % self.game_size,
                                   (self.dealer_count + 2) % self.game_size]
        ante_players = [self.game.players[idx]
                        for idx in next_two_player_indices]

        self.transfer_to_pot(ante_players[0], self.little_ante)
        self.transfer_to_pot(ante_players[1], self.big_ante)
        ante_players[0].current_raise = self.little_ante
        ante_players[1].current_raise = self.big_ante
        self.set_current_bettor((self.dealer_count + 3) % self.game_size)
        self.current_wager = self.big_ante
        self.last_raise_player = ante_players[1]
        self.bets.append(Bet(player=ante_players[0], amount=self.little_ante))
        self.bets.append(Bet(player=ante_players[1], amount=self.big_ante))

        print(f"little blind {ante_players[0]} paid {self.little_ante}")
        print(f"big blind {ante_players[1]} paid {self.big_ante}")

        self.advance_phase(GamePhase.ANTE_PAID)

    def set_current_bettor(self, idx):
        logging.debug(f"bettor set to {idx}, last raise from {self.last_raise_player}")
        self.bettor_index = idx

    def advance_bettor(self):
        new_bettor_idx = (self.bettor_index + 1) % self.round_size
        self.set_current_bettor(new_bettor_idx)

    def advance_phase(self, new_phase: GamePhase):
        print(f"advancing from {self.game_state} to {new_phase}")
        self.game_state = new_phase

    def transfer_to_pot(self, player: Player, ante: int):
        if player.current_bank >= ante:
            self.pot += ante
            player.current_bank -= ante
        else:
            raise NotEnoughMoneyToContinue(player)

    def deal_players_two_cards(self):
        for player in self.game.players:
            player.cards = self.deck.draw(2)

        self.advance_phase(GamePhase.WAITING_ON_BET)

    def solicit_next_bet(self):
        player = self.round_players[self.bettor_index]
        to_match = self.current_wager - player.current_wager

        print(f"player {player.handle} turn to bet, current wager {player.current_wager}, {to_match} to match")

        player_marginal_hand_value_guess = random.randint(0, 5) * 5
        print(f"player {player.handle} guesses value at {player_marginal_hand_value_guess}")

        if self.current_wager - player_marginal_hand_value_guess > 0:
            self.fold_player(player)
        else:
            self.place_bet(player, player_marginal_hand_value_guess)

        self.advance_bettor()
        return True

    def fold_player(self, player):
        print(f"player {player.handle} folds")
        self.round_size -= 1
        self.round_players.remove(player)

    def place_bet(self, player, marginal_bet):
        print(f"player {player.handle} bets {marginal_bet}")
        self.transfer_to_pot(player, marginal_bet)
        player.current_wager += marginal_bet
        self.current_wager = player.current_wager
        self.last_raise_player = player
        self.bets.append(Bet(player=player, amount=marginal_bet))

    def award_pot(self, player):
        player.current_bank += self.pot
        self.pot = 0

    def reset_bets(self):
        self.current_wager = 0
        self.last_raise_player = None
        for player in self.round_players:
            player.current_wager = 0
