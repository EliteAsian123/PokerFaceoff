from __future__ import annotations
from typing import TYPE_CHECKING

# We only need these for type checking. Prevents circular imports.
if TYPE_CHECKING:
    from server.client_handler import ClientHandler
    from server.server import Server

from common.public_game_state import PublicPlayer
from common.cards import Card
from common.actions import Action
from server.logger import log_client_action

class Player:
    data: PublicPlayer
    pocket_cards: list[Card]

    _client_handler: ClientHandler

    def __init__(self, client_handler: ClientHandler, id: int, name: str):
        self.data = PublicPlayer(id=id, name=name)
        self.pocket_cards = []
        self._client_handler = client_handler

    def get_client_handler_if_valid(self, server: Server) -> ClientHandler | None:
        """A Player's ClientHandler will not be valid if the Player is still in the game but the client has disconnected from the server."""
        if server.is_client_handler_valid(self._client_handler):
            return self._client_handler

    def reset(self):
        self.data.reset()
        self.pocket_cards = []

    def do_blind(self, up_to):
        self.data.current_bet = up_to
        log_client_action(f"{self.data.name} bet ${up_to} for the blind.")

    def do_fold(self):
        self.data.folded = True
        log_client_action(f"{self.data.name} folded.")

    def do_show(self):
        log_client_action(f"{self.data.name} shows their cards.")

    def do_check(self):
        log_client_action(f"{self.data.name} checked.")

    def do_call(self, up_to):
        self.data.current_bet = up_to
        log_client_action(f"{self.data.name} called ${up_to}.")

    def do_raise(self, up_to):
        self.data.current_bet = up_to
        log_client_action(f"{self.data.name} raised to ${up_to} total.")

    def illegal(self, action, explaination):
        self.data.folded = True
        log_client_action(f"{self.data.name} performed an illegal action '{action}'. {explaination}")
