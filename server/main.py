from server.player import *
from server.game_state import *
from common.actions import *
from common.server_response import *
from common.client_response import *
from enum import Enum, auto
from websockets import ConnectionClosed, ServerConnection, serve
import asyncio
import sys

class ServerState(Enum):
    LOBBY = auto()

state: ServerState = ServerState.LOBBY
players: list[Player] = []
players_to_remove: list[Player] = []
joined_names: set[str] = set()

def remove_excess_players():
    global players
    global players_to_remove

    for p in players:
        if p in players_to_remove:
            players.remove(p)
            joined_names.remove(p.data.name.lower())

    players_to_remove.clear()

async def send(ws: ServerConnection, model: ServerResponse):
    await ws.send(model.model_dump_json(), True)

async def handle_lobby(ws: ServerConnection, player: Player | None, data: ClientResponse) -> Player | None:
    global players
    global joined_names

    match data.action:
        case Join(name=name):
            if player != None:
                raise ValueError(f"You have already joined!")

            if name.lower() in joined_names:
                raise ValueError(f"A player with the name '{name}' has already joined.")

            player = Player(ws, name)
            players.append(player)
            joined_names.add(name.lower())

            log_important(f"Connection {ws.remote_address} joined as '{name}'")
            await send(ws, ServerResponse(action=JoinSuccess()))
        case _:
            raise ValueError("You must join before performing any action.")

    return player

# A new handler is created for each client
async def handler(ws: ServerConnection):
    log_important(f"Connnection opened with {ws.local_address}")

    global state
    global players
    global players_to_remove

    player: Player | None = None
    try:
        async for raw_message in ws:
            data = ClientResponse.model_validate_json(raw_message)
            match state:
                case ServerState.LOBBY:
                    player = await handle_lobby(ws, player, data)
    except ConnectionClosed:
        if player == None:
            log_important(f"Connnection closed with {ws.remote_address}")
        else:
            log_important(f"Connnection closed with {ws.remote_address} '{player.data.name}'")
            players_to_remove.append(player)
    except Exception as e:
        if player == None:
            log_important(f"Error with {ws.remote_address}: {e}")
        else:
            log_important(f"Error with {ws.remote_address} '{player.data.name}': {e}")
            players_to_remove.append(player)

        try:
            await send(ws, ServerResponse(action=ServerError(message=str(e))))
            await ws.close()
        except:
            pass

async def main():
    global players

    expected_player_count = int(sys.argv[1])
    async with serve(handler, "localhost", 8001):
        log_important("Running server at ws://localhost:8001")
        log_important(f"Waiting until {expected_player_count} are present before starting the game.")

        while True:
            while len(players) < expected_player_count:
                await asyncio.sleep(0.5)
                remove_excess_players()

            log_important("Starting round...")

if __name__ == "__main__":
    asyncio.run(main())
