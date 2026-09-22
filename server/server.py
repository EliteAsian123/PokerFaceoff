from server.player import Player
from server.game_state import GameState
from server.client_handler import ClientHandler
from server.logger import log_important
from server.server_state import ServerState
from common.server_response import ServerResponse, RoundStarting
from websockets import ServerConnection, serve
import asyncio

class Server:
    state: ServerState

    # Important note: we need to separate players and client handlers. A player leaving during
    # a middle of the poker game is not allowed so the player must stay in the game. However,
    # a ClientHandler disconnecting is allowed.

    _client_handlers: list[ClientHandler]

    _players: list[Player]
    _players_to_remove: list[Player]
    _joined_names: set[str]

    def __init__(self):
        self.state = ServerState.LOBBY

        self._client_handlers = []

        self._players = []
        self._players_to_remove = []
        self._joined_names = set()

    async def start(self, expected_player_count: int, step_mode: bool):
        # We need to use a lambda as we need a closure with self
        async with serve(lambda ws: self.__handler(ws), "localhost", 8001):
            log_important("Running server at ws://localhost:8001")
            log_important(f"Waiting until {expected_player_count} are present before starting the game.")

            while True:
                while len(self._players) < expected_player_count:
                    await asyncio.sleep(0.5)
                    self.remove_queued_players()

                await asyncio.sleep(0.5)
                log_important(f"Starting round with {len(self._players)} players...")

                for p in self._client_handlers:
                    await p.send(ServerResponse(action=RoundStarting()))

                game_state = GameState(self._players, step_mode)
                game_state.start_round()

    async def __handler(self, ws: ServerConnection):
        # A new handler is created for each client
        handler = ClientHandler(ws)
        self._client_handlers.append(handler)
        await handler.start_handler(self)

    def disconnect_client_handler(self, handler: ClientHandler):
        self._client_handlers.remove(handler)

    def is_client_handler_valid(self, handler: ClientHandler) -> bool:
        return handler in self._client_handlers

    def add_player(self, player: Player):
        if player.data.name.lower() in self._joined_names:
            raise ValueError(f"A player with the name '{player.data.name}' has already joined.")

        self._players.append(player)
        self._joined_names.add(player.data.name.lower())

    def queue_player_removal(self, player: Player):
        self._players_to_remove.append(player)

    def remove_queued_players(self):
        for p in self._players:
            if p in self._players_to_remove:
                self._players.remove(p)
                self._joined_names.remove(p.data.name.lower())

        self._players_to_remove.clear()
