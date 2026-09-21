from server.player import *
from server.game_state import *

def main():
    players = [
        Player("Alex"),
        Player("Andrew"),
        Player("Graham"),
        Player("Julia"),
        Player("Mark"),
    ]
    state = GameState(players, False)
    state.start_round()
    pass

if __name__ == "__main__":
    main()
