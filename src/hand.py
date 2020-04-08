from dataclasses import dataclass
from typing import List

from deuces import Card


# Dumb helper class to pretty-print hands because
# deuces uses List[int] for cards
@dataclass
class Hand:
    cards: List[int]

    def push_cards(self, cards: List[int]):
        self.cards.extend(cards)

    def __repr__(self):
        return Card.cards_as_str(self.cards)
