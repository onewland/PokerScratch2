import uuid
from dataclasses import dataclass, field
from uuid import UUID

from hand import Hand


@dataclass
class Player:
    handle: str
    hand: Hand
    id: UUID = field(default_factory=lambda: uuid.uuid4())
    bought_in_total: int = 1000
    current_bank: int = 1000
    current_wager: int = 0
