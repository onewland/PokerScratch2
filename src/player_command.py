from dataclasses import dataclass


@dataclass
class PlayerCommand:
    checkpoint: str

@dataclass
class RaiseCommand(PlayerCommand):
    new_wager: int

class FoldCommand(PlayerCommand):
    pass

class CallCommand(PlayerCommand):
    pass

class CheckCommand(PlayerCommand):
    pass

class BuyInCommand(PlayerCommand):
    pass

class HaltGameCommand(PlayerCommand):
    pass