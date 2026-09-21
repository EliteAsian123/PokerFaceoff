from common.cards import Card

class PublicPlayer:
    name: str
    folded: bool
    current_bet: int
    pocket_cards: list[Card] | None

    def __init__(self, name: str):
        self.name = name
        self.folded = False
        self.current_bet = 0
        self.pocket_cards = None

    def reset(self):
        self.folded = False
        self.current_bet = 0
        self.pocket_cards = None

class PublicGameState:
    community_cards: list[Card]
    pot: int
    previous_bet: int
    small_blind_index: int

    def __init__(self):
        self.community_cards = []
        self.pot = 0
        self.previous_bet = 0
        self.small_blind_index = -1
