# GameService controls the flow of a single game within a session
# handling draw and reveal of cards, and passing off to BettingRound
# when that is necessary
from enum import Enum

from betting_round import BettingRound
from deuces import Evaluator, Card
from game import Game
from hand import Hand
from player import Player
from player_rotation import PlayerRotation


# Consider changing this from Enum to each one being a
# subclass which records phase + phase change behavior
class GamePhase(Enum):
    DEALING_CARDS_1_2 = 1
    DEALING_FLOP = 2
    DEALING_TURN = 3
    DEALING_RIVER = 4
    ONE_MAN_REMAINING = 5
    RESOLVE_HANDS_FORCEFULLY = 6
    WINNER_SET = 7


class GameService:
    winner: Player

    def __init__(self, *, game: Game, dealer_index=0):
        self.pot_total = 0
        self.game = game
        self.players = self.game.players
        self.min_raise = game.big_ante
        self.round_rotation = PlayerRotation(
            players=self.players, start_index=dealer_index
        )
        self.phase = GamePhase.DEALING_CARDS_1_2
        self.inside_betting_round = False
        self.current_betting_round = BettingRound(
            game=game, betting_rotation=self.round_rotation, last_raise_option=True
        )
        self.shared_cards = []
        self.winner = None
        self.evaluator = Evaluator()
        for player in self.players:
            player.hand = Hand([])

    def is_game_end(self):
        return (
            self.phase == GamePhase.ONE_MAN_REMAINING
            or self.phase == GamePhase.RESOLVE_HANDS_FORCEFULLY
            or self.phase == GamePhase.WINNER_SET
        )

    # advances to next phase of game if ready, returns True if a phase change occurred
    # and false if not
    def advance_phase_if_ready(self) -> (GamePhase, bool):
        if self.is_game_end():
            return self.phase, False

        if self.inside_betting_round and self.current_betting_round.is_settled_up():
            if self.phase == GamePhase.DEALING_CARDS_1_2:
                self.resolve_round(self.current_betting_round)
                self.inside_betting_round = False
                self.phase = GamePhase.DEALING_FLOP
                self.deal_flop()
                return self.phase, True
            elif self.phase == GamePhase.DEALING_FLOP:
                self.resolve_round(self.current_betting_round)
                self.inside_betting_round = False
                self.phase = GamePhase.DEALING_TURN
                self.deal_turn()
                return self.phase, True
            elif self.phase == GamePhase.DEALING_TURN:
                self.resolve_round(self.current_betting_round)
                self.inside_betting_round = False
                self.phase = GamePhase.DEALING_RIVER
                self.deal_river()
                return self.phase, True
            elif self.phase == GamePhase.DEALING_RIVER:
                self.resolve_round(self.current_betting_round)
                self.phase = GamePhase.RESOLVE_HANDS_FORCEFULLY
                self.compare_hands_and_set_winner()
                return self.phase, True

        if len(self.round_rotation.players) == 1:
            self.resolve_round(self.current_betting_round)
            self.phase = GamePhase.ONE_MAN_REMAINING
            self.set_one_man_winner()
            return self.phase, True

        return self.phase, False

    # Deals first two cards, then forcibly antes for first two players in dealer rotation
    def deal_cards_1_2(self):
        for player in self.players:
            player.hand.push_cards(self.game.deck.draw(2))

        # Advance past player at start_index (dealer)
        self.current_betting_round.advance_player()

        # Wager little and big ante for player start + 1, start + 2
        self.current_betting_round.player_increase_wager_and_advance(
            self.current_betting_round.current_bettor, self.game.little_ante
        )
        self.current_betting_round.player_increase_wager_and_advance(
            self.current_betting_round.current_bettor, self.game.big_ante
        )

        # Yield control to betting round
        self.inside_betting_round = True

    def resolve_round(self, current_betting_round):
        # move funds to pot
        self.pot_total += current_betting_round.round_pot
        # create a new betting round
        self.current_betting_round = BettingRound(
            betting_rotation=self.round_rotation,
            game=self.game,
            min_raise=self.min_raise,
        )

    def compare_hands_and_set_winner(self):
        min_rank = 8000
        top_player = None
        for player in self.round_rotation.players:
            Card.print_pretty_cards(player.hand.cards + self.shared_cards)
            player_rank = self.evaluator.evaluate(player.hand.cards, self.shared_cards)
            if player_rank < min_rank:
                min_rank = player_rank
                top_player = player
        self.set_winner(top_player)

    def set_one_man_winner(self):
        remaining_player = self.round_rotation.players[0]
        self.set_winner(remaining_player)

    def set_winner(self, player):
        self.winner = player
        self.phase = GamePhase.WINNER_SET

    def deal_flop(self):
        self._deal_n_shared_cards(3)

    def deal_turn(self):
        self._deal_n_shared_cards(1)

    def deal_river(self):
        self._deal_n_shared_cards(1)

    def _deal_n_shared_cards(self, n):
        draw = self.game.deck.draw(n)
        if isinstance(draw, int):
            draw = [draw]
        self.shared_cards.extend(draw)
        self.inside_betting_round = True

    def dict_repr(self):
        return {
            "betting_round": self.current_betting_round.dict_repr(),
            "phase": self.phase.name,
            "shared_cards": self.shared_cards,
            "inside_betting_round": self.inside_betting_round,
            "winner": self.winner,
        }

    def shared_as_nice_str(self):
        return Card.cards_as_str(self.shared_cards)
