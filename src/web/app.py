from flask import Flask, request

import config
from command_evaluator import CommandEvaluator
from deuces import Deck
from game import Game
from game_service import GameService
from hand import Hand
from player import Player
from player_command import RaiseCommand, FoldCommand, CallCommand, CheckCommand

app = Flask(__name__)
config.load_config(app)
player_names = ["alfred", "betty", "chris", "dee"]
players = [Player(name, hand=Hand([])) for name in player_names]
game = Game(players, Deck(), little_ante=5, big_ante=10)
service = GameService(game=game)
command_evaluator = CommandEvaluator(service)

service.deal_cards_1_2()


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/v1/game", methods=["GET"])
def get_game_service_game_state():
    return service.dict_repr()


@app.route("/v1/game/raise", methods=["POST"])
def player_raise():
    command = request.get_json()
    new_wager_amount = command["new_wager_amount"]
    player_id = command["player_id"]
    checkpoint_id = command["checkpoint_id"]

    result = command_evaluator.process_raise(
        RaiseCommand(
            new_wager=new_wager_amount, checkpoint=checkpoint_id, player_id=player_id
        )
    )
    return {"service": service.dict_repr(), "commandResult": result}


@app.route("/v1/game/fold", methods=["POST"])
def player_fold():
    command = request.get_json()
    player_id = command["player_id"]
    checkpoint_id = command["checkpoint_id"]

    result = command_evaluator.process_fold(
        FoldCommand(checkpoint=checkpoint_id, player_id=player_id)
    )
    return {"service": service.dict_repr(), "commandResult": result}


@app.route("/v1/game/call", methods=["POST"])
def player_call():
    command = request.get_json()
    player_id = command["player_id"]
    checkpoint_id = command["checkpoint_id"]

    result = command_evaluator.process_call(
        CallCommand(checkpoint=checkpoint_id, player_id=player_id)
    )
    return {"service": service.dict_repr(), "commandResult": result}


@app.route("/v1/game/call", methods=["POST"])
def player_check():
    command = request.get_json()
    player_id = command["player_id"]
    checkpoint_id = command["checkpoint_id"]

    result = command_evaluator.process_check(
        CheckCommand(checkpoint=checkpoint_id, player_id=player_id)
    )
    return {"service": service.dict_repr(), "commandResult": result}
