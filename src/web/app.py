import uuid

from flask import Flask, request, render_template, session

import config
from command_evaluator import CommandEvaluator
from deuces import Deck
from game import Game
from hand import Hand
from player import Player
from player_command import RaiseCommand, FoldCommand, CallCommand, CheckCommand, NextGameCommand
from player_manager import PlayerManager
from game_session import GameSession

app = Flask(__name__)
config.load_config(app)
player_names = ["alfred", "betty", "chris", "dee"]
players = [Player(handle=name, hand=Hand([]), id=uuid.uuid4())
           for name in player_names]
player_manager = PlayerManager(players)
print(players)
game = Game(players, Deck(), little_ante=10, big_ante=20)
game_session = GameSession(game=game)

command_evaluator = CommandEvaluator(game_session)
game_session.current_round.deal_cards_1_2()

service = game_session.current_round
app.secret_key = config.SECRET

@app.route("/god_mode")
def friendly_god_game_view():
    return render_template('root_template.html', session=game_session)

@app.route("/")
def player_view():
    player = player_manager.get_player_by_id(session['player_id'])
    app.logger.info(f"player ID = {session['player_id']}")
    return render_template('player_view.html', session=game_session, player=player)

@app.route("/v1/game", methods=["GET"])
def get_game_service_game_state():
    player = player_manager.get_player_by_id(session['player_id'])
    return {'player': player, 'game': service.dict_repr()}

@app.route("/v1/auth_by_name/<name>", methods=['POST', 'GET'])
def set_session_player_by_name(name):
    player = player_manager.get_player_by_handle(name)
    session['player_id'] = player.id
    return {'auth': 'success', 'player_id': player.id}

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


@app.route("/v1/game/check", methods=["POST"])
def player_check():
    command = request.get_json()
    player_id = command["player_id"]
    checkpoint_id = command["checkpoint_id"]

    result = command_evaluator.process_check(
        CheckCommand(checkpoint=checkpoint_id, player_id=player_id)
    )
    return {"service": service.dict_repr(), "commandResult": result}


@app.route("/v1/session/next_game", methods=["POST"])
def proceed_to_next_game():
    command = request.get_json()
    player_id = command["player_id"]
    checkpoint_id = command["checkpoint_id"]

    result = command_evaluator.process_next_game(
        NextGameCommand(checkpoint=checkpoint_id, player_id=player_id)
    )
    return {"service": service.dict_repr(), "commandResult": result}

@app.route("/v1/session/start_next_game", methods=["POST"])
def deal_next_game():
    command = request.get_json()
    player_id = command["player_id"]
    checkpoint_id = command["checkpoint_id"]

    result = command_evaluator.process_next_game(
        NextGameCommand(checkpoint=checkpoint_id, player_id=player_id)
    )
    return {"service": service.dict_repr(), "commandResult": result}

@app.route("/v1/session/terminate", methods=["POST"])
def end_session():
    x = game_session.end_session()

    return {"service": service.dict_repr(), "commandResult": x}
