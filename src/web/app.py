import flask
from flask import Flask

import game_orchestrator
from deuces import Deck
from game import Game
from player import Player

app = Flask(__name__)

player_names = ["oliver", "josh", "tyler", "wilfred"]
players = [Player(name, []) for name in player_names]
game = Game(players, Deck())
orchestrator = game_orchestrator.HoldemGameLoop(game, little_ante=5, big_ante=10)

orchestrator.advance_if_possible()


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/game', methods=['GET'])
def echo_game_id():
    return {'game': orchestrator.json_dict()}


@app.route('/game/advance', methods=['POST'])
def advance():
    if orchestrator.advance_if_possible():
        return {'game': 'continues'}
    else:
        return {'game': 'over'}
