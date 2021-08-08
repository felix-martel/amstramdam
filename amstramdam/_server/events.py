from amstramdam._server.main import socketio


@socketio.on("connection")
def join_game():
    """
    The player connects to the game room for the first time.

     To do:
    - initialize the game (if it doesn't exist yet)
    - add the player to the room
    - warn other players
    """
    pass


@socketio.on("disconnect")
def leave_game():
    """
    The player leaves the game room

    Todo:
    - remove the player from the game
    - warn other players
    - if the game no longer has players, remove the game
    """
    pass


@socketio.on("request-game-change")
def change_game():
    """
    The player changes the game map (at the end of a game)

    Todo:
    - create new game
    - redirect player to the new game
    - warn players to join the new game
    """
    pass


@socketio.on("name-change")
def change_player_name():
    """
    The player requests a name change

    Todo:
    - rename the player
    - warn other players
    """


@socketio.on("chat:send")
def process_chat_message():
    """
    The player sends a chat message

    Todo:
    - broadcast it to other players
    """
    pass


@socketio.on("launch")
def launch_game():
    """
    The player launches the game

    Todo:
    - launch the game (including starting timeouts)
    - warn players
    """
    pass


@socketio.on("guess")
def process_guess():
    """
    The players submits a guess

    Todo:
    - process guess
    - send feedback
    - warn other players
    """
    pass

