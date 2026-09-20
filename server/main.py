from common.iter_clockwise import iter_clockwise, enumerate_clockwise
from common.cards import Card, Rank, Suit, deck_shuffled
from common.actions import *
from server.player import Player
from server.logger import *

SMALL_BLIND = 1
BIG_BLIND = 2

class State:
    step_mode: bool
    deck: list[Card]
    community_cards: list[Card]
    players: list[Player]
    pot: int
    previous_bet: int
    small_blind_index: int

    def __init__(self, step_mode: bool, players: list[Player]):
        self.step_mode = step_mode
        self.deck = []
        self.community_cards = []
        self.players = players
        self.pot = 0
        self.previous_bet = 0
        self.small_blind_index = -1

    def start_round(self):
        self.__pre_flop_stage()

    def __step(self):
        if self.step_mode:
            input()

    def __pretty_print(self, action_index: int | None = None):
        """
        Log out the current state of the game.
        """
        def pretty_cards(cards: list[Card]):
            if len(cards) == 0:
                return "N/A"
            return " ".join([card.ansi_string() for card in cards])

        log()
        log(f"Pot: ${self.pot} | Previous Bet: ${self.previous_bet}")

        log()
        log(f"Community Cards: {pretty_cards(self.community_cards)}")

        log()
        for i, p in enumerate(self.players):
            action_pointer = " "
            if i == action_index:
                action_pointer = "*"

            if p.folded:
                log(f"{action_pointer} {p.name:<8} [FOLDED]")
            else:
                log(f"{action_pointer} {p.name:<8} (Bet: ${p.current_bet})   {pretty_cards(p.pocket_cards)}")

        log()

    def __win(self, player: Player):
        log_server_action(f"{player.name} wins!")

    def __pot_bets(self):
        for p in self.players:
            self.pot += p.current_bet
            p.current_bet = 0

    def __play(self, start_index: int) -> bool:
        """
        Go around the table and allow players to place their bets.

        Returns:
            True if someone has won. False if no one has won yet.
        """
        while True:
            for i, player in enumerate_clockwise(self.players, start_index):
                if player.folded:
                    continue

                self.__pretty_print(i)
                self.__step()

                action = player.action(self.previous_bet)
                self.__process_action(player, action)

                # See if anyone has won
                potential_winner = None
                unfolded_amount = 0
                for player in self.players:
                    if not player.folded:
                        potential_winner = player
                        unfolded_amount += 1

                # If only one person remains and they haven't folded, they won
                if unfolded_amount == 1:
                    self.__pot_bets()
                    self.__win(potential_winner)
                    return True

            # A round of play does not end until all players have folded, all players
            # put in all of their chips, or all players matched the amount put in by all
            # other players.
            for p in self.players:
                if p.folded:
                    continue
                if p.current_bet == self.previous_bet:
                    continue
                # TODO if all in
                break
            else:
                self.__pot_bets()
                return False

    def __process_action(self, player: Player, action: Action):
        """
        Process a player's action.
        """
        match action:
            case Fold():
                player.do_fold()
            case Bet(up_to=up_to):
                if up_to < self.previous_bet or up_to < player.current_bet:
                    player.illegal(
                        action,
                        f"You bet less than the current bet of ${self.previous_bet}."
                    )
                elif up_to == player.current_bet:
                    player.do_check()
                elif up_to == self.previous_bet:
                    player.do_call(up_to)
                elif up_to < self.previous_bet * 2:
                    player.illegal(
                        action,
                        f"You must (re)raise at least two times the current bet (${self.previous_bet} * 2 = ${self.previous_bet})."
                    )
                else:
                    player.do_raise(up_to)
                    self.previous_bet = up_to
            case AllIn():
                pass # TODO

    def __pre_flop_stage(self):
        log_server_action("Pre-flop stage.")

        # Reset game state
        self.deck = deck_shuffled()
        self.community_cards = []
        for player in self.players:
            player.reset()
        self.pot = 0
        self.previous_bet = BIG_BLIND
        self.small_blind_index += 1

        # Blind bets
        small_blind_index = self.small_blind_index % len(self.players)
        big_blind_index = (self.small_blind_index + 1) % len(self.players)
        self.players[small_blind_index].do_blind(SMALL_BLIND)
        self.players[big_blind_index].do_blind(BIG_BLIND)

        # Deal pocket cards
        for _ in range(2):
            for player in iter_clockwise(self.players, self.small_blind_index):
                player.pocket_cards.append(self.deck.pop())

        if self.__play((self.small_blind_index + 2) % len(self.players)):
            return

        self.__flop_stage()

    def __flop_stage(self):
        log_server_action("Flop stage.")

        # Reset game state
        self.previous_bet = 0

        # Burn and turn
        self.deck.pop()
        for _ in range(3):
            self.community_cards.append(self.deck.pop())

        if self.__play(self.small_blind_index % len(self.players)):
            return

        self.__turn_stage()

    def __turn_stage(self):
        log_server_action("Turn stage.")

        # Reset game state
        self.previous_bet = 0

        # Burn and turn
        self.deck.pop()
        self.community_cards.append(self.deck.pop())

        if self.__play(self.small_blind_index % len(self.players)):
            return

        self.__river_stage()

    def __river_stage(self):
        log_server_action("River stage.")

        # Reset game state
        self.previous_bet = 0

        # Burn and turn
        self.deck.pop()
        self.community_cards.append(self.deck.pop())

        if self.__play(self.small_blind_index % len(self.players)):
            return

def main():
    players = [
        Player("Alex"),
        Player("Andrew"),
        Player("Graham"),
        Player("Julia"),
        Player("Mark"),
    ]
    state = State(True, players)
    state.start_round()
    pass

if __name__ == "__main__":
    main()
