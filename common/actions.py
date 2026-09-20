from typing import Literal

class Fold:
    type: Literal["fold"]

    def __init__(self):
        self.type = "fold"

    def __repr__(self):
        return "Fold"

class Show:
    type: Literal["show"]

    def __init__(self):
        self.type = "show"

    def __repr__(self):
        return "Show"

class Bet:
    type: Literal["bet"]
    up_to: int

    def __init__(self, up_to: int):
        self.type = "bet"
        self.up_to = up_to

    def __repr__(self):
        return f"Bet(up_to={self.up_to})"

class AllIn:
    type: Literal["allIn"]

    def __init__(self):
        self.type = "allIn"

    def __repr__(self):
        return f"AllIn"

Action = Fold | Show | Bet | AllIn
