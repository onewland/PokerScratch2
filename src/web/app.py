import flask
from flask import Flask, request

import game_orchestrator
from deuces import Deck
from game import Game
from game_service import GameService
from hand import Hand
from player import Player

app = Flask(__name__)

player_names = ["oliver", "josh", "tyler", "wilfred"]
players = [Player(name, hand=Hand([])) for name in player_names]
game = Game(players, Deck(), little_ante=5, big_ante=10)
orchestrator = game_orchestrator.HoldemGameLoop(game, little_ante=5, big_ante=10)
service = GameService(game=game)
service.deal_cards_1_2()


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/game", methods=["GET"])
def echo_game_id():
    return {"game": orchestrator.json_dict()}


@app.route("/game/advance", methods=["POST"])
def advance():
    if orchestrator.advance_if_possible():
        return {"game": "continues"}
    else:
        return {"game": "over"}


@app.route("/v1/game", methods=["GET"])
def get_game_service_game_state():
    return service.dict_repr()


@app.route("/v1/game/command", methods=["POST"])
def submit_command():
    print(request.get_json())
    print(players[0])
    return service.dict_repr()
