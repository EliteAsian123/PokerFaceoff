from dataclasses import dataclass
from enum import Enum, auto
from functools import total_ordering
from itertools import combinations
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
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

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

# ===== HAND EVALUATION =====
class HandType(Enum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8

    def __str__(self) -> str:
        match self:
            case HandType.HIGH_CARD:
                return "High Card"
            case HandType.ONE_PAIR:
                return "Pair"
            case HandType.TWO_PAIR:
                return "Two Pair"
            case HandType.THREE_OF_A_KIND:
                return "Three of a Kind"
            case HandType.STRAIGHT:
                return "Straight"
            case HandType.FLUSH:
                return "Flush"
            case HandType.FULL_HOUSE:
                return "Full House"
            case HandType.FOUR_OF_A_KIND:
                return "Four of a King"
            case HandType.STRAIGHT_FLUSH:
                return "Straight Flush"

@dataclass()
@total_ordering
class Hand:
    type: HandType
    cards: list[Card]

    def __eq__(self, other):
        return self.type.value == other.type.value

    def __lt__(self, other):
        return self.type.value < other.type.value

    def __str__(self):
        cards = " ".join(str(c) for c in self.cards)
        return f"{str(self.type)} ({cards})"

    def ansi_string(self):
        cards = " ".join(c.ansi_string() for c in self.cards)
        return f"{str(self.type)} ({cards})"

def rank_value(card: Card) -> int:
    return card.rank.value

def is_flush(cards: list[Card]) -> bool:
    for card in cards:
        if card.suit != cards[0].suit:
            return False

    return True

def is_straight(cards: list[Card]) -> bool:
    card_values = []
    for card in cards:
        card_values.append(rank_value(card))

    card_values.sort()

    # A to 5 straight case
    if card_values == [2, 3, 4, 5, 14]:
        return True

    # Any other straight
    for x in range(4):
        if card_values[x] + 1 != card_values[x + 1]:
            return False

    return True

def evaluate_hand(cards: list[Card]) -> HandType:
    card_values = []
    for card in cards:
        card_values.append(rank_value(card))

    # count the times each rank appears
    counts = []

    for value in card_values:
        if value not in counts:
            counts.append(value)

    pairs = 0
    trips = False
    quads = False

    for value in counts:
        amount = card_values.count(value)
        if amount == 2:
            pairs += 1
        elif amount == 3:
            trips = True
        elif amount == 4:
            quads = True

    flush = is_flush(cards)
    straight = is_straight(cards)

    if straight and flush:
        return HandType.STRAIGHT_FLUSH

    if quads:
        return HandType.FOUR_OF_A_KIND

    if trips and pairs == 1:
        return HandType.FULL_HOUSE

    if flush:
        return HandType.FLUSH

    if straight:
        return HandType.STRAIGHT

    if trips:
        return HandType.THREE_OF_A_KIND

    if pairs == 2:
        return HandType.TWO_PAIR

    if pairs == 1:
        return HandType.ONE_PAIR

    else:
        return HandType.HIGH_CARD

def find_best_hand(cards: list[Card]) -> Hand:
    # Find best hand possible with 2 held cards + 5 community cards
    best = None

    for five_cards in combinations(cards, 5):
        five_cards = list(five_cards)

        hand_type = evaluate_hand(five_cards)

        if best is None or hand_type.value > best.type.value:
            best = Hand(hand_type, five_cards)
    return best

# ===== EXAMPLE USAGE ====
if __name__ == "__main__":
    deck_of_cards = deck_shuffled()

    five_cards = [deck_of_cards.pop() for _ in range(5)]
    player1 = [deck_of_cards.pop() for _ in range(2)]
    player2 = [deck_of_cards.pop() for _ in range(2)]

    print("Community CArds:")
    print(" ".join(c.ansi_string() for c in five_cards))

    print("\n Player 1:")
    print(" ".join(c.ansi_string() for c in player1))

    print("\n Player 2:")
    print(" ".join(c.ansi_string() for c in player2))

    hand1 = find_best_hand(player1 + five_cards)
    hand2 = find_best_hand(player2 + five_cards)

    print("\nPlayer 1:", hand1.type.name)
    print("Cards:", " ".join(str(card) for card in hand1.cards))

    print("\nPlayer 2:", hand2.type.name)
    print("Cards:", " ".join(str(card) for card in hand2.cards))

    if hand1 > hand2:
        print("\nPlayer 1 wins!")
    elif hand2 > hand1:
        print("\nPlayer 2 wins!")
    else:
        print("\nTie!") # TODO
