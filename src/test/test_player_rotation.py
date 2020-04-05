import unittest

import player
from hand import Hand
from player_rotation import PlayerRotation


class TestPlayerRotation(unittest.TestCase):
    def setUp(self) -> None:
        self.players = [
            player.Player(hand=Hand([]), handle=f"p{n}") for n in range(1, 4)
        ]
        self.player_rotation = PlayerRotation(self.players)

    def test_advance_circles(self):
        self.assertEqual(self.player_rotation.get_current_player(), self.players[0])
        self.player_rotation.advance()
        self.assertEqual(self.player_rotation.get_current_player(), self.players[1])
        self.player_rotation.advance()
        self.assertEqual(self.player_rotation.get_current_player(), self.players[2])
        self.player_rotation.advance()
        self.assertEqual(self.player_rotation.get_current_player(), self.players[0])

    def test_remove_current_player(self):
        self.assertEqual(self.player_rotation.get_current_player(), self.players[0])
        self.player_rotation.remove_current()
        self.assertEqual(self.player_rotation.get_current_player(), self.players[1])

    def test_remove_last_player_while_current(self):
        self.player_rotation.advance()
        self.player_rotation.advance()
        self.assertEqual(self.player_rotation.get_current_player(), self.players[2])

        self.player_rotation.remove_current()
        self.assertEqual(self.player_rotation.get_current_player(), self.players[0])
