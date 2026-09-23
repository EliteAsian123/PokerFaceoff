from common.public_game_state import PublicGameData, PublicPlayer

DISPLAY_NAME = "Template Bot"

def pre_join():
    """Called before the bot joins the game. Useful for configuring bot settings via `input`."""
    pass

def start_round(data: PublicGameData, me: PublicPlayer):
    """Called at the start of the round.

    Args:
        data: An instance of `PublicGameData` representing the state of the game.
        me: An instance of `PublicPlayer` representing this bot's player state. This exact instance is guarenteed to be within `data.players`.
    """
    print()
    print(f"The round has started!")
    print()
    print(f"data=PublicGameData({data})")
    print()
    print(f"me=PublicPlayer({me})")
