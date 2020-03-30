from dataclasses import dataclass
from typing import List

from deuces import Deck
from player import Player


@dataclass
class Game:
    players: List[Player]
    deck: Deck
    turn_counter: int = 0