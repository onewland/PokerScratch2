from typing import Dict, List

from player import Player


class PlayerManager:
    players_by_id: Dict[str, Player] = {}
    players_by_handle: Dict[str, Player] = {}

    def __init__(self, players: List[Player]):
        for player in players:
            self.add_player(player)

    def add_player(self, player: Player):
        self.players_by_id[player.id] = player
        self.players_by_handle[player.handle] = player

    def get_player_by_id(self, player_id: str) -> Player:
        return self.players_by_id[player_id]

    def get_player_by_handle(self, player_id: str) -> Player:
        return self.players_by_handle[player_id]