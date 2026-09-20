import random
from server.player import Player
from common.cards import Card, Rank, Suit, deck_shuffled
import common.actions as actions

SMALL_BLIND = 1
BIG_BLIND = 2

class State:
    deck: list[Card]
    players: list[Player]
    pot: int
    highest_bet: int
    blind_index: int

    def __init__(self, players: list[Player]):
        self.deck = []
        self.players = players
        self.pot = 0
        self.highest_bet = 0
        self.blind_index = -1

    def start_round(self):
        self._pre_flop_hand()

    def _pretty_print(self):
        def pretty_cards(cards: list[Card]):
            return " ".join([card.ansi_string() for card in cards])

        print(f"Pot: ${self.pot} | Current Bet: ${self.highest_bet}\n")

        for p in self.players:
            if p.folded:
                print(f"{p.name:<8} [FOLDED]")
            else:
                print(f"{p.name:<8} (Bet: ${p.current_bet})   {pretty_cards(p.hand)}")

        print()

    def _process_action(self, player, action):
        match action:
            case actions.Fold:
                player.do_fold()
            case actions.Bet(up_to=up_to):
                if up_to < self.highest_bet or up_to < player.current_bet:
                    player.illegal(
                        action,
                        f"You bet less than the current bet of ${self.highest_bet}."
                    )
                elif up_to == player.current_bet:
                    player.do_check()
                elif up_to == self.highest_bet:
                    player.do_call(up_to)
                elif up_to < self.highest_bet * 2:
                    player.illegal(
                        action,
                        f"You must (re)raise at least two times the current bet (${self.highest_bet} * 2 = ${self.highest_bet})."
                    )
                else:
                    player.do_raise(up_to)
                    self.highest_bet = up_to
            case actions.AllIn:
                pass # TODO

    def _pre_flop_hand(self):
        self.deck = deck_shuffled()
        for player in self.players:
            player.reset()
        self.pot = 0
        self.highest_bet = BIG_BLIND
        self.blind_index += 1

        small_blind_index = self.blind_index % len(self.players)
        big_blind_index = (self.blind_index + 1) % len(self.players)

        self.players[small_blind_index].force_bet(SMALL_BLIND)
        self.players[big_blind_index].force_bet(BIG_BLIND)

        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.pop())

        self._pretty_print()

        for player in self.players:
            action = player.action()
            self._process_action(action)

def main():
    players = [
        Player("Alex"),
        Player("Andrew"),
        Player("Graham"),
        Player("Julia"),
        Player("Mark"),
    ]
    state = State(players)
    state.start_round()
    pass

if __name__ == "__main__":
    main()
