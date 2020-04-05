from dataclasses import dataclass
from typing import List

from deuces import Deck
from player import Player

# A Game represents one hand dealt and [potentially] resolved to a conclusion
# Each Game is part of a Session
# Each Game proceeds through up to 4 BettingRound(s)
@dataclass
class Game:
    players: List[Player]
    deck: Deck
    little_ante: int
    big_ante: int
