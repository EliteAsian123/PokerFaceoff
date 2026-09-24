from common.actions import Action, Fold, Show, Bet, AllIn
from common.public_game_state import PublicGameData, PublicPlayer

DISPLAY_NAME = "Template Bot"

def pre_join():
    """Called before the bot joins the game. Useful for configuring bot settings via `input`."""
    pass

def start_round(data: PublicGameData, me: PublicPlayer):
    """Called at the start of the round.

    Args:
        data: An instance of `PublicGameData` representing the current state of the game.
        me: An instance of `PublicPlayer` representing this bot's player state. This exact instance is guarenteed to be within `data.players`.
    """
    print("The round has started!")

def action(data: PublicGameData, me: PublicPlayer) -> Action:
    """Called when it's the bot's turn.

    Returns:
        The action that the bot should take.

    Args:
        data: An instance of `PublicGameData` representing the current state of the game.
        me: An instance of `PublicPlayer` representing this bot's player state. This exact instance is guarenteed to be within `data.players`.
    """
    print("Folding...")
    return Fold()
