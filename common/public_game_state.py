from pydantic import BaseModel
from common.cards import Card

class PublicGameState(BaseModel):
    community_cards: list[Card] = []
    pot: int = 0
    previous_bet: int = 0
    small_blind_index: int = -1

class PublicPlayer(BaseModel):
    id: int
    name: str
    folded: bool = False
    current_bet: int = 0
    revealed_pocket_cards: list[Card] | None = None

    def reset(self):
        self.folded = False
        self.current_bet = 0
        self.revealed_pocket_cards = None

class PublicGameData(BaseModel):
    state: PublicGameState
    players: list[PublicPlayer]
