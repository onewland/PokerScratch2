from dataclasses import dataclass


@dataclass
class PlayerCommand:
    checkpoint: str
    player_id: str


@dataclass
class RaiseCommand(PlayerCommand):
    new_wager: int


@dataclass
class FoldCommand(PlayerCommand):
    pass


@dataclass
class CallCommand(PlayerCommand):
    pass


@dataclass
class CheckCommand(PlayerCommand):
    pass

@dataclass
class NextGameCommand(PlayerCommand):
    pass

@dataclass
class EndSessionCommand(PlayerCommand):
    pass

@dataclass
class StartNextGameCommand(PlayerCommand):
    pass