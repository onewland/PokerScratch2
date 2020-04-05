from typing import List

from player import Player


class PlayerRotation:
    def __init__(self, players: List[Player], start_index=0):
        self.players_original = players
        self.players = players
        self.current_player_idx = start_index

    def player_count(self) -> int:
        return len(self.players)

    def advance(self) -> Player:
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        return self.get_current_player()

    def get_current_player(self) -> Player:
        if len(self.players) > 0:
            return self.players[self.current_player_idx]
        else:
            raise PlayerRotationEmpty()

    def remove_current(self) -> None:
        self.remove(self.players[self.current_player_idx])

    def remove(self, player) -> None:
        if self.players[self.current_player_idx] == player:
            self.advance()
        self.players.remove(player)


class PlayerRotationEmpty(BaseException):
    pass
