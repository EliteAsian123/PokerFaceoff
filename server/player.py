from common.cards import Card
from common.actions import *
from server.logger import *
import random

class Player:
    name: str
    pocket_cards: list[Card]
    current_bet: int
    folded: bool

    def __init__(self, name):
        self.name = name
        self.pocket_cards = []
        self.current_bet = 0
        self.folded = False

    def reset(self):
        self.pocket_cards = []
        self.current_bet = 0
        self.folded = False

    def do_blind(self, up_to):
        self.current_bet = up_to
        log_client_action(f"{self.name} bet ${up_to} for the blind.")

    def do_fold(self):
        self.folded = True
        log_client_action(f"{self.name} folded.")

    def do_check(self):
        log_client_action(f"{self.name} checked.")

    def do_call(self, up_to):
        self.current_bet = up_to
        log_client_action(f"{self.name} called ${up_to}.")

    def do_raise(self, up_to):
        self.current_bet = up_to
        log_client_action(f"{self.name} raised to ${up_to} total.")

    def illegal(self, action, explaination):
        self.folded = True
        log_client_action(f"{self.name} performed an illegal action '{action}'. {explaination}")

    def action(self, current_bet: int) -> Action:
        log_server_action(f"Action on {self.name}.")
        if random.randint(1, 8) == 1:
            return Bet(max(current_bet * 2, 2))
        return Bet(current_bet)
