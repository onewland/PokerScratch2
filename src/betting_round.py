import uuid
from typing import Any, Dict

from game import Game
from player import Player
from player_rotation import PlayerRotation


class InsufficientBetException(BaseException):
    pass


class DataValidationException(Exception):
    data: Dict[str, Any]

    def __init__(self, **kwargs):
        self.data = kwargs


class InvalidWagerAdjustment(DataValidationException):
    def __init__(self, **kwargs):
        self.data = kwargs


class InsufficientPlayerFunds(DataValidationException):
    def __init__(self, **kwargs):
        self.data = kwargs


class BettingRound:
    min_raise: int

    def __init__(
        self,
        betting_rotation: PlayerRotation,
        game: Game,
        last_raise_option: bool = False,
        min_raise: int = 1,
    ) -> object:
        self.min_raise = min_raise
        self.id = uuid.uuid4().hex
        self.current_wager = 0
        self.round_pot = 0
        self.last_raise_player = None
        self.betting_rotation = betting_rotation
        self.current_bettor = betting_rotation.get_current_player()
        # does the last raiser have option to raise again?
        # (true for big blind in first round of a game)
        self.last_raise_option = last_raise_option
        self.game = game
        self.round_finished = False

    def is_settled_up(self):
        if self.round_finished:
            return True

        if (
            self.current_bettor == self.last_raise_player
            or len(self.betting_rotation.players) == 1
        ):
            return not self.last_raise_option
        else:
            return False

    def advance_player(self) -> None:
        if self.last_raise_option and self.current_bettor == self.last_raise_player:
            self.round_finished = True
            return

        if self.current_bettor.current_wager < self.current_wager:
            raise InsufficientBetException(
                current_wager=self.current_wager,
                player_wager=self.current_bettor.current_wager,
            )
        if self.last_raise_player is None:
            self.last_raise_player = self.current_bettor
        self.current_bettor = self.betting_rotation.advance()

    def player_increase_wager_and_advance(self, player, adjusted_wager: int):
        if (
            self.current_wager > adjusted_wager
            or player.current_wager > adjusted_wager
            or adjusted_wager - player.current_wager < self.min_raise
        ):
            raise InvalidWagerAdjustment(
                table_wager=self.current_wager,
                player_wager=player.current_wager,
                adjusted_wager=adjusted_wager,
                min_raise=self.min_raise,
            )
        else:
            adjustment = adjusted_wager - player.current_wager
            self.adjust_player_wager(player, adjustment)
            self.advance_player()

    def player_call_and_advance(self, player):
        adjustment = self.current_wager - player.current_wager
        self.adjust_player_wager(player, adjustment)
        self.advance_player()

    def player_check_and_advance(self, player):
        if player.current_wager == self.current_wager:
            self.advance_player()

    def player_fold(self, player):
        self.betting_rotation.remove(player)

    def adjust_player_wager(self, player: Player, adjustment):
        if player.current_bank - adjustment >= 0:
            self.round_pot += adjustment
            player.current_wager += adjustment
            player.current_bank -= adjustment
        else:
            raise InsufficientPlayerFunds(player=player, adjustment=adjustment)

    def dict_repr(self):
        return {
            "round_pot": self.round_pot,
            "finished": self.round_finished,
            "current_wager": self.current_wager,
            "current_bettor": self.current_bettor,
        }
