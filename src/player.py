from dataclasses import dataclass
from typing import List

import deuces
from deuces import Deck


@dataclass
class Player:
    handle: str
    cards: List[deuces.Card]
    bought_in_total: int = 100
    current_bank: int = 100
    current_wager: int = 0

@dataclass
class Game:
    players: List[Player]
    deck: Deck
    turn_counter: int = 0
