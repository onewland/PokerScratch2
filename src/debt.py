from dataclasses import dataclass

from player import Player


@dataclass(frozen=True)
class Debt:
    debtor: Player
    owed: Player
    amount: int