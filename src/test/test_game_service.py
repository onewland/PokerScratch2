import unittest
from unittest import mock
from unittest.mock import MagicMock

from deuces import deck, Deck
from game import Game
from game_service import GameService, GamePhase
from hand import Hand
from player import Player


class TestGameService(unittest.TestCase):
    def setUp(self) -> None:
        self.players = [Player(handle=f"p{n}", hand=Hand([])) for n in range(1, 5)]
        self.game = Game(little_ante=25, big_ante=50, players=self.players, deck=Deck())
        self.game_service = GameService(game=self.game)

    def test_deal_1_2_deals_cards_and_bets_moves_to_inside_betting(self):
        self.game_service.deal_cards_1_2()
        self.assertEqual(self.game_service.current_betting_round.round_pot, 75)
        self.assertEqual(
            self.game_service.current_betting_round.current_bettor, self.players[3]
        )
        self.assertTrue(self.game_service.inside_betting_round)

        phase, changed = self.game_service.advance_phase_if_ready()
        self.assertFalse(changed)
        self.assertEqual(phase, GamePhase.DEALING_CARDS_1_2)

    def test_betting_round_done_after_deal_1_2_shifts_river(self):
        self.game_service.deal_cards_1_2()
        self.game_service.current_betting_round.round_finished = True

        phase, changed = self.game_service.advance_phase_if_ready()
        self.assertTrue(changed)
        self.assertEqual(phase, GamePhase.DEALING_FLOP)
