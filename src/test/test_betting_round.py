import unittest
import unittest.mock

import player
from betting_round import (
    BettingRound,
    InvalidWagerAdjustment,
    InsufficientPlayerFunds,
)
from hand import Hand
from player_rotation import PlayerRotation


class TestBettingRound(unittest.TestCase):
    def setUp(self) -> None:
        self.START_BANK = 25
        self.MIN_RAISE = 5
        self.players = [
            player.Player(hand=Hand([]), handle=f"p{n}", current_bank=self.START_BANK)
            for n in range(1, 4)
        ]
        self.player1 = self.players[0]
        self.player2 = self.players[1]
        self.player_rotation = PlayerRotation(self.players)
        self.game = unittest.mock.Mock()
        self.betting_round = BettingRound(
            game=self.game,
            betting_rotation=self.player_rotation,
            min_raise=self.MIN_RAISE,
        )

    def test_is_settled_up_should_be_false(self):
        self.assertFalse(self.betting_round.is_settled_up())

    def test_is_settled_up_should_be_true_when_advanced_to_end_no_option(self):
        self.betting_round.last_raise_player = self.players[0]
        self.betting_round.advance_player()
        self.betting_round.advance_player()
        self.betting_round.advance_player()

        self.assertTrue(self.betting_round.is_settled_up())

    def test_is_settled_up_should_be_true_when_advanced_to_end_with_option(self):
        option_round = BettingRound(
            game=self.game,
            betting_rotation=self.player_rotation,
            last_raise_option=True,
        )
        option_round.advance_player()
        option_round.last_raise_player = self.players[0]
        option_round.advance_player()
        option_round.advance_player()

        self.assertFalse(option_round.is_settled_up())

        option_round.advance_player()
        self.assertTrue(option_round.is_settled_up())

    @unittest.skip
    def bet_too_small(self):
        BET = 1
        self.betting_round.player_increase_wager_and_advance(self.player1, BET)

    def test_raise_too_small_raises_exception(self):
        self.assertRaises(InvalidWagerAdjustment, self.bet_too_small())

    def test_raise_happy_path(self):
        self.betting_round.player_increase_wager_and_advance(
            self.player1, self.MIN_RAISE
        )

        self.assertEqual(self.player1.current_bank, self.START_BANK - self.MIN_RAISE)
        self.assertEqual(self.betting_round.round_pot, self.MIN_RAISE)
        self.assertEqual(self.betting_round.current_bettor, self.player2)

    def test_raise_insufficient_funds_raises_exception(self):
        self.assertRaises(InsufficientPlayerFunds, self.bet_too_rich())

    @unittest.skip
    def bet_too_rich(self):
        self.betting_round.player_increase_wager_and_advance(
            self.player1, self.START_BANK * 2
        )
