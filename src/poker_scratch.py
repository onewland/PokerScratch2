from deuces import Deck
from game_orchestrator import HoldemGameLoop
from player import Player
from game import Game

player_names = ["oliver", "josh", "tyler", "wilfred"]


def main():
    players = [Player(name, []) for name in player_names]
    game = Game(players, Deck())
    orchestrator = HoldemGameLoop(game, little_ante=5, big_ante=10)
    while orchestrator.advance_if_possible():
        print(orchestrator)
    print(orchestrator.bets)


def print_evaluation(evaluator, hand):
    rank_class = evaluator.get_rank_class(evaluator.evaluate(hand, []))
    as_string = evaluator.class_to_string(rank_class)
    print(f"{as_string} - {rank_class}")


if __name__ == "__main__":
    main()
