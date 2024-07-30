from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from client import sio

app = Flask(__name__)
socketio = SocketIO(app)

# Dictionary to store player names with their respective session IDs
player_names = {}
game_manager = None  # To store the game manager's name
general_data = {}

@socketio.on('submit_name')
def handle_submit_name(data):
    global game_manager
    player_name = data['name']
    session_id = request.sid  # Get the session ID of the current client

    if not game_manager:
        game_manager = player_name

    player_names[session_id] = player_name
    print(game_manager)
    emit('update_names', {'names': list(player_names.values()), 'game_manager': game_manager}, broadcast=True)

# Add the 'start_game' event handler
@socketio.on('start_game')
def handle_start_game():
    emit('game_started', broadcast=True)

# Handling the update_general event
@socketio.on('update_general')
def update_general(data):
    global general_data
    general_data = data.get('general', {})
    emit('general_updated', {'general': general_data}, broadcast=True)

@socketio.on('update_roles')
def update_roles(data):
    roles = data.get('roles', {})
    emit('roles_updated', {'roles': roles}, broadcast=True)

from threading import Lock

update_lock = Lock()

@socketio.on('update_ready')
def update_ready(data):
    try:
        with update_lock:
            ready = data.get('ready', {})
            emit('ready_updated', {'ready': ready}, broadcast=True)
    except Exception as e:
        print(f"Error processing update: {e}")

@socketio.on('update_wolf')
def update_wolf(data):
    wolf = data.get('wolf', {})
    emit('wolf_updated', {'wolf': wolf}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)