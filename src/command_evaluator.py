from dataclasses import dataclass
from typing import List

import config
import player_command
from debt import Debt
from game_service import GameService, GamePhase
from session import Session


@dataclass(frozen=True)
class CommandResult:
    success: bool


@dataclass(frozen=True)
class CommandResultSessionOver(CommandResult):
    payouts: List[Debt]


@dataclass(frozen=True)
class CommandResultNotInBettingRound(CommandResult):
    phase: GamePhase


class CommandEvaluator:
    game_service: GameService

    def __init__(self, session: Session):
        self.session = session

    @property
    def game_service(self) -> GameService:
        return self.session.current_round

    def process_raise(self, command: player_command.RaiseCommand):
        if not self.game_service.inside_betting_round:
            return CommandResultNotInBettingRound(
                phase=self.game_service.phase, success=False
            )

        if config.BYPASS_SAFETY_CHECKPOINTS:
            betting_round = self.game_service.current_betting_round
            bettor = betting_round.current_bettor
            betting_round.player_increase_wager_and_advance(bettor, command.new_wager)
            self.game_service.advance_phase_if_ready()
            return CommandResult(success=True)
        else:
            raise NotImplementedError("can't do turn enforcement yet")

    def process_fold(self, command: player_command.FoldCommand) -> CommandResult:
        if not self.game_service.inside_betting_round:
            return CommandResultNotInBettingRound(
                phase=self.game_service.phase, success=False
            )

        if config.BYPASS_SAFETY_CHECKPOINTS:
            betting_round = self.game_service.current_betting_round
            bettor = betting_round.current_bettor
            betting_round.player_fold(bettor)
            self.game_service.advance_phase_if_ready()
            return CommandResult(success=True)
        else:
            raise NotImplementedError("can't do turn enforcement yet")

    def process_call(self, command: player_command.CallCommand) -> CommandResult:
        if not self.game_service.inside_betting_round:
            return CommandResultNotInBettingRound(
                phase=self.game_service.phase, success=False
            )

        if config.BYPASS_SAFETY_CHECKPOINTS:
            betting_round = self.game_service.current_betting_round
            bettor = betting_round.current_bettor
            betting_round.player_call_and_advance(bettor)
            self.game_service.advance_phase_if_ready()
            return CommandResult(success=True)
        else:
            raise NotImplementedError("can't do turn enforcement yet")

    def process_check(self, command: player_command.CheckCommand) -> CommandResult:
        if not self.game_service.inside_betting_round:
            return CommandResultNotInBettingRound(
                phase=self.game_service.phase, success=False
            )

        if config.BYPASS_SAFETY_CHECKPOINTS:
            betting_round = self.game_service.current_betting_round
            bettor = betting_round.current_bettor
            betting_round.player_check_and_advance(bettor)
            self.game_service.advance_phase_if_ready()
            return CommandResult(success=True)
        else:
            raise NotImplementedError("can't do turn enforcement yet")

    def process_next_game(self, command: player_command.NextGameCommand) -> CommandResult:
        round_did_finish = self.session.distribute_round_funds()
        if round_did_finish:
            return CommandResult(success=True)

        return CommandResult(success=False)

    def process_start_next_game(self, command: player_command.StartNextGameCommand) -> CommandResult:
        return CommandResult(success=self.session.start_next_round_if_ready())

    def process_end_session(self, command: player_command.EndSessionCommand) -> CommandResultSessionOver:
        return CommandResultSessionOver(success=True, debts=self.session.end_session())
