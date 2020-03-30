from flask import Flask
import json
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/games/<string:game_id>', methods=['GET'])
def echo_game_id(game_id):
    return json.dumps({'game_id': game_id})