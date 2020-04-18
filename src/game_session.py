from typing import List

from debt import Debt
from game import Game
from game_service import GameService
from player_rotation import PlayerRotation


class ImpossibleCondition(Exception):
    pass


class GameSession:
    def __init__(self, *, game: Game):
        self.dealer_rotation = PlayerRotation(game.players)
        self.game = game
        self.current_round = GameService(game=game,
                                         dealer_index=self.dealer_rotation.current_player_idx)
        self.distributed_funds = False
        self.terminated = False

    def start_next_round_if_ready(self):
        if self.distributed_funds:
            self.dealer_rotation.advance()
            self.current_round = GameService(game=self.game,
                                             dealer_index=self.dealer_rotation.current_player_idx)
            self.distributed_funds = False
            self.current_round.deal_cards_1_2()
            return True
        else:
            return False

    def distribute_round_funds(self) -> bool:
        if self.current_round.winner:
            winner = self.current_round.winner
            winner.current_bank += self.current_round.pot_total
            self.distributed_funds = True
            return True
        else:
            return False

    def end_session(self) -> List[Debt]:
        self.terminated = True
        total_player_offset = 0
        owing_players = []
        owed_players = []
        debts = []

        for player in self.game.players:
            player_offset = player.current_bank - player.bought_in_total
            if player_offset == 0:
                continue
            if player_offset < 0:
                owing_players.append((player, player_offset))
            else:
                owed_players.append((player, player_offset))
            total_player_offset += player_offset

        if total_player_offset != 0:
            raise ImpossibleCondition()

        owing_players.sort(key=lambda x: x[1])
        owed_players.sort(key=lambda x: x[1])

        owed_player_idx = 0
        for debtor_offset in owing_players:
            debtor, debt_remaining = debtor_offset[0], abs(debtor_offset[1])

            while debt_remaining > 0:
                owed_player, owed = owed_players[owed_player_idx]
                if debt_remaining >= owed:
                    debts.append(Debt(debtor=debtor.handle, owed=owed_player.handle, amount=owed))
                    debt_remaining -= owed
                    owed_player_idx += 1
                else:
                    debts.append(Debt(debtor=debtor.handle, owed=owed_player.handle, amount=debt_remaining))
                    debt_remaining = 0

        return debts
