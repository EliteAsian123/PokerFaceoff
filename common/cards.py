from dataclasses import dataclass
from enum import Enum, auto
import random

class Suit(Enum):
    SPADES = auto()
    HEARTS = auto()
    DIAMONDS = auto()
    CLUBS = auto()

    def symbol(self) -> str:
        return {
            Suit.SPADES: "♠",
            Suit.HEARTS: "♥",
            Suit.DIAMONDS: "♦",
            Suit.CLUBS: "♣",
        }[self]

    def is_black(self) -> bool:
        return self in (Suit.SPADES, Suit.CLUBS)

    def is_red(self) -> bool:
        return not self.is_black()

class Rank(Enum):
    ACE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
    NINE = auto()
    TEN = auto()
    JACK = auto()
    QUEEN = auto()
    KING = auto()

    def symbol(self) -> str:
        match self:
            case Rank.ACE:
                return "A "
            case Rank.JACK:
                return "J "
            case Rank.QUEEN:
                return "Q "
            case Rank.KING:
                return "K "
            case Rank.TEN:
                return "10"
            case _:
                return str(self.value) + " "

@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        return f"{self.suit.symbol()}{self.rank.symbol()}"

    def __repr__(self) -> str:
        return f"Card(suit={self.suit}, rank={self.rank})"

    def ansi_string(self) -> str:
        """
        Return a string with ANSI color codes for console printing.

        Black suits (spades, clubs) are white, red suits (hearts, diamonds) are red.
        """
        color_code = "\033[97m" if self.suit.is_black() else "\033[31m"
        reset_code = "\033[0m"
        return f"{color_code}{self.suit.symbol()}{self.rank.symbol()}{reset_code}"

def random_card() -> Card:
    """
    Generate a random card from a standard 52-card deck.
    """
    return Card(
        rank=random.choice(list(Rank)),
        suit=random.choice(list(Suit))
    )

def deck() -> list[Card]:
    """
    Generate a full deck of 52 cards in order.
    """
    deck = []
    for rank in Rank:
        for suit in Suit:
            deck.append(Card(rank=rank, suit=suit))
    return deck

def deck_shuffled() -> list[Card]:
    d = deck()
    random.shuffle(d)
    return d

# ===== EXAMPLE USAGE ====
if __name__ == "__main__":
    deck_of_cards = deck_shuffled()

    five_cards = [deck_of_cards.pop() for _ in range(5)]
    player1 = [deck_of_cards.pop() for _ in range(2)]
    player2 = [deck_of_cards.pop() for _ in range(2)]

    print(" ".join(c.ansi_string() for c in five_cards))
    print(" ".join(c.ansi_string() for c in player1))
    print(" ".join(c.ansi_string() for c in player2))
