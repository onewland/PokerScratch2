from dataclasses import dataclass
from typing import List

from deuces import Card


@dataclass
class Hand:
    cards: List[int]

    def push_cards(self, cards: List[int]):
        self.cards.extend(cards)

    def __repr__(self):
        print(self.cards)
        return Card.cards_as_str(self.cards)
