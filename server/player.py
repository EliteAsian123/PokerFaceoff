from common.cards import Card
import common.actions as actions
from enum import Enum, auto

class Player:
    name: str
    hand: list[Card]
    current_bet: int
    folded: bool

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.current_bet = 0
        self.folded = False

    def reset(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False

    def do_fold(self):
        self.folded = True
        print(f"> {self.name} folded.")

    def do_check(self):
        print(f"> {self.name} checked.")

    def do_call(self, up_to):
        print(f"> {self.name} called up to ${up_to}.")

    def do_raise(self, up_to):
        print(f"> {self.name} raised up to ${up_to}.")

    def illegal(self, action, explaination):
        self.folded = True
        print(f"> {self.name} performed an illegal action '{action}'. {explaination}")

    def action(self) -> actions.Action:
        return actions.Fold()
