from dataclasses import dataclass
from typing import List

import deuces


@dataclass
class Player:
    handle: str
    cards: List[deuces.Card]
    bought_in_total: int = 1000
    current_bank: int = 1000
    current_wager: int = 0

