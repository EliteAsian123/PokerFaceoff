from common.public_game_state import *
from common.actions import *
from common.iter_clockwise import iter_clockwise, enumerate_clockwise
from common.cards import Hand, deck_shuffled, find_best_hand
from server.logger import *
from server.player import *
from copy import copy

SMALL_BLIND = 1
BIG_BLIND = 2

class GameState:
    data: PublicGameState
    players: list[Player]
    deck: list[Card]
    step_mode: bool

    def __init__(self, players: list[Player], step_mode: bool):
        self.data = PublicGameState()
        self.players = players
        self.deck = []
        self.step_mode = step_mode

    def create_public_data(self, player: Player | None) -> PublicGameData:
        players: list[Player] = []
        for p in self.players:
            data = copy(p.data)
            if p == player:
                data.revealed_pocket_cards = player.pocket_cards
            players.append(data)

        return PublicGameData(
            state=copy(self.data),
            players=players
        )

    async def start_round(self) -> list[Player]:
        return await self.__pre_flop_stage()

    def __step(self):
        if self.step_mode:
            input()

    def __pretty_print(self, action_index: int | None = None):
        """Log the current state of the game."""
        def pretty_cards(cards: list[Card]):
            if len(cards) == 0:
                return "N/A"
            return " ".join([card.ansi_string() for card in cards])

        log()
        log(f"Pot: ${self.data.pot} | Previous Bet: ${self.data.previous_bet}")

        log()
        log(f"Community Cards: {pretty_cards(self.data.community_cards)}")

        log()
        for i, p in enumerate(self.players):
            action_pointer = " "
            if i == action_index:
                action_pointer = "*"

            if p.data.folded:
                log(f"{action_pointer} {p.data.name:<15} [FOLDED]")
            else:
                log(f"{action_pointer} {p.data.name:<15} (Bet: ${p.data.current_bet})   {pretty_cards(p.pocket_cards)}")

        log()

    def __win(self, player: Player, reason: str):
        log_server_action(f"{player.data.name} wins! {reason}")

    def __pot_bets(self):
        for p in self.players:
            self.data.pot += p.data.current_bet
            p.data.current_bet = 0

    async def __play(self, start_index: int) -> Player | None:
        """Go around the table and allow players to place their bets.

        Returns:
            True if someone has won. False if no one has won yet.
        """
        while True:
            for i, player in enumerate_clockwise(self.players, start_index):
                if player.data.folded:
                    continue

                self.__pretty_print(i)
                self.__step()

                action = await player.action(self.create_public_data(player))
                self.__process_action(player, action)

                # See if anyone has won
                potential_winner = None
                unfolded_amount = 0
                for player in self.players:
                    if not player.data.folded:
                        potential_winner = player
                        unfolded_amount += 1

                # If only one person remains and they haven't folded, they won
                if unfolded_amount == 1:
                    self.__pot_bets()
                    self.__win(potential_winner, "Everyone else folded.")
                    return potential_winner

            # A round of play does not end until all players have folded, all players
            # put in all of their chips, or all players matched the amount put in by all
            # other players.
            for p in self.players:
                if p.data.folded:
                    continue
                if p.data.current_bet == self.data.previous_bet:
                    continue
                # TODO if all in
                break
            else:
                self.__pot_bets()
                return None

    def __process_action(self, player: Player, action: Action):
        """Process a player's action."""
        match action:
            case Join():
                player.illegal(
                    action,
                    f"You have already joined."
                )
            case Fold():
                player.do_fold()
            case Show():
                player.illegal(
                    action,
                    f"You showed your hand before the showdown."
                )
            case Bet(up_to=up_to):
                if up_to < self.data.previous_bet or up_to < player.data.current_bet:
                    player.illegal(
                        action,
                        f"You bet less than the current bet of ${self.data.previous_bet}."
                    )
                elif up_to == player.data.current_bet:
                    player.do_check()
                elif up_to == self.data.previous_bet:
                    player.do_call(up_to)
                elif up_to < self.data.previous_bet * 2:
                    player.illegal(
                        action,
                        f"You must (re)raise at least two times the current bet (${self.data.previous_bet} * 2 = ${self.data.previous_bet})."
                    )
                else:
                    player.do_raise(up_to)
                    self.data.previous_bet = up_to
            case AllIn():
                raise NotImplemented

    async def __pre_flop_stage(self) -> list[Player]:
        log_server_action("Pre-flop stage.")

        # Reset game state
        self.deck = deck_shuffled()
        self.data.community_cards = []
        for player in self.players:
            player.reset()
        self.data.pot = 0
        self.data.previous_bet = BIG_BLIND
        self.data.small_blind_index += 1
        self.data.game_stage = GameStage.PRE_FLOP

        # Blind bets
        small_blind_index = self.data.small_blind_index % len(self.players)
        big_blind_index = (self.data.small_blind_index + 1) % len(self.players)
        self.players[small_blind_index].do_blind(SMALL_BLIND)
        self.players[big_blind_index].do_blind(BIG_BLIND)

        # Deal pocket cards
        for _ in range(2):
            for player in iter_clockwise(self.players, self.data.small_blind_index):
                player.pocket_cards.append(self.deck.pop())

        potential_winner = await self.__play((self.data.small_blind_index + 2) % len(self.players))
        if potential_winner is not None:
            return [potential_winner]

        return await self.__flop_stage()

    async def __flop_stage(self) -> list[Player]:
        log_server_action("Flop stage.")

        # Reset game state
        self.data.previous_bet = 0
        self.data.game_stage = GameStage.FLOP

        # Burn and turn
        self.deck.pop()
        for _ in range(3):
            self.data.community_cards.append(self.deck.pop())

        potential_winner = await self.__play(self.data.small_blind_index % len(self.players))
        if potential_winner is not None:
            return [potential_winner]

        return await self.__turn_stage()

    async def __turn_stage(self) -> list[Player]:
        log_server_action("Turn stage.")

        # Reset game state
        self.data.previous_bet = 0
        self.data.game_stage = GameStage.TURN

        # Burn and turn
        self.deck.pop()
        self.data.community_cards.append(self.deck.pop())

        potential_winner = await self.__play(self.data.small_blind_index % len(self.players))
        if potential_winner is not None:
            return [potential_winner]

        return await self.__river_stage()

    async def __river_stage(self) -> list[Player]:
        log_server_action("River stage.")

        # Reset game state
        self.data.previous_bet = 0
        self.data.game_stage = GameStage.RIVER

        # Burn and turn
        self.deck.pop()
        self.data.community_cards.append(self.deck.pop())

        potential_winner = await self.__play(self.data.small_blind_index % len(self.players))
        if potential_winner is not None:
            return [potential_winner]

        return await self.__showdown_stage()

    async def __showdown_stage(self) -> list[Player]:
        log_server_action("Showdown stage.")

        # Reset game state
        self.data.previous_bet = 0
        self.data.game_stage = GameStage.SHOWDOWN

        for i, player in enumerate_clockwise(self.players, self.data.small_blind_index % len(self.players)):
            self.__pretty_print(i)
            self.__step()

            action = await player.action(self.create_public_data(player))
            match action:
                case Fold():
                    player.do_fold()
                case Show():
                    player.do_show()
                case _:
                    player.illegal(
                        action,
                        "You cannot do this in the showdown."
                    )
            pass

        player_hands: list[Hand | None] = []
        for player in self.players:
            if player.data.folded:
                player_hands.append(None)
            else:
                player_hands.append(find_best_hand(self.data.community_cards + player.pocket_cards))

        highest_hands_players = []
        for i in range(len(self.players)):
            if player_hands[i] is None:
                continue

            if len(highest_hands_players) == 0 or player_hands[i] == player_hands[highest_hands_players[0]]:
                highest_hands_players.append(i)
            elif player_hands[i] > player_hands[highest_hands_players[0]]:
                highest_hands_players = [i]

        if len(highest_hands_players) == 1:
            winner = self.players[highest_hands_players[0]]
            self.__win(
                winner,
                f"Won with a {player_hands[highest_hands_players[0]].ansi_string()}."
            )
            return [winner]
        else:
            log_server_action("Tie!")
            raise NotImplemented
