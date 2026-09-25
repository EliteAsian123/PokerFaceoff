from __future__ import annotations
from typing import TYPE_CHECKING

# We only need these for type checking. Prevents circular imports.
if TYPE_CHECKING:
    from server.server import Server

from common.client_response import ClientResponse
from common.server_response import ServerResponse, JoinSuccess, ServerError
from common.client_response import Action
from common.actions import Join
from server.player import Player
from server.server_state import ServerState
from server.logger import log_important
from websockets import ServerConnection, ConnectionClosed
import asyncio

class ClientHandler:
    player: Player | None
    id: int
    ws: ServerConnection

    _last_processed_action: Action | None

    def __init__(self, id: int, ws: ServerConnection):
        self.player = None
        self.id = id
        self.ws = ws

        self._last_processed_action = None

    async def send(self, model: ServerResponse):
        await self.ws.send(model.model_dump_json(), True)

    async def wait_until_action(self) -> Action:
        SLEEP_TIME = 0.1

        max_time = 10.0
        if self.player.disable_time_limit:
            max_time = float("inf")

        time = 0
        while time < max_time:
            if self._last_processed_action is not None:
                result = self._last_processed_action
                self._last_processed_action = None
                return result

            await asyncio.sleep(SLEEP_TIME)
            time += SLEEP_TIME
        return None

    async def __handle_lobby(self, server: Server, data: ClientResponse):
        match data.action:
            case Join(name=name, disable_time_limit=disable_time_limit):
                if self.player is not None:
                    raise ValueError(f"You have already joined!")

                self.player = Player(self, self.id, name, disable_time_limit)
                server.add_player(self.player)

                log_important(f"Connection {self.ws.remote_address} joined as '{name}'")
                await self.send(ServerResponse(action=JoinSuccess(id=self.id)))
            case _:
                raise ValueError("You must join before performing any action.")

    def __handle_game(self, data: ClientResponse):
        match data.action:
            case _:
                self._last_processed_action = data.action

    async def start_handler(self, server: Server):
        log_important(f"Connnection opened with {self.ws.local_address}")

        try:
            async for raw_message in self.ws:
                data = ClientResponse.model_validate_json(raw_message)
                match server.state:
                    case ServerState.LOBBY:
                        await self.__handle_lobby(server, data)
                    case ServerState.GAME:
                        self.__handle_game(data)
        except ConnectionClosed:
            if self.player is None:
                log_important(f"Connnection closed with {self.ws.remote_address}")
            else:
                log_important(f"Connnection closed with {self.ws.remote_address} '{self.player.data.name}'")
                server.queue_player_removal(self.player)
        except Exception as e:
            if self.player is None:
                log_important(f"Error with {self.ws.remote_address}: {e}")
            else:
                log_important(f"Error with {self.ws.remote_address} '{self.player.data.name}': {e}")
                server.queue_player_removal(self.player)

            try:
                await self.send(ServerResponse(action=ServerError(message=str(e))))
                await self.ws.close()
            except:
                pass
        finally:
            server.disconnect_client_handler(self)
