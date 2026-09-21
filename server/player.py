from common.public_game_state import *
from common.actions import *
from server.logger import *
from websockets import ServerConnection
import random

class Player:
    ws: ServerConnection
    data: PublicPlayer
    pocket_cards: list[Card]

    def __init__(self, ws: ServerConnection, name: str):
        self.ws = ws
        self.data = PublicPlayer(name)
        self.pocket_cards = []

    def reset(self):
        self.data.reset()
        self.pocket_cards = []

    def do_blind(self, up_to):
        self.data.current_bet = up_to
        log_client_action(f"{self.data.name} bet ${up_to} for the blind.")

    def do_fold(self):
        self.data.folded = True
        log_client_action(f"{self.data.name} folded.")

    def do_show(self):
        log_client_action(f"{self.data.name} shows their cards.")

    def do_check(self):
        log_client_action(f"{self.data.name} checked.")

    def do_call(self, up_to):
        self.data.current_bet = up_to
        log_client_action(f"{self.data.name} called ${up_to}.")

    def do_raise(self, up_to):
        self.data.current_bet = up_to
        log_client_action(f"{self.data.name} raised to ${up_to} total.")

    def illegal(self, action, explaination):
        self.data.folded = True
        log_client_action(f"{self.data.name} performed an illegal action '{action}'. {explaination}")

    def action(self, current_bet: int, show_down: bool) -> Action:
        log_server_action(f"Action on {self.data.name}.")
        if show_down:
            return Show()
        if random.randint(1, 8) == 1:
            return Bet(max(current_bet * 2, 2))
        return Bet(current_bet)
