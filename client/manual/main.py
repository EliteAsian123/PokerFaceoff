from websockets import ClientConnection, ConnectionClosed
from common.cards import Card
from common.client_response import ClientResponse
from common.public_game_state import PublicGameData, PublicPlayer
from common.server_response import RoundEnd, ServerResponse, ServerError, JoinSuccess, RoundStarting, YourTurn
from common.actions import Bet, Fold, Join, Show
from websockets.asyncio.client import connect
import asyncio
import sys
import os

async def send(ws: ClientConnection, model: ClientResponse):
    await ws.send(model.model_dump_json(), True)

async def recv(ws: ClientConnection) -> ServerResponse:
    response = await ws.recv()
    return ServerResponse.model_validate_json(response)

def get_me(data: PublicGameData, self_id: int) -> PublicPlayer:
    for p in data.players:
        if p.id == self_id:
            return p
    raise ValueError(f"Could not find player data with ID {self_id} in game data.")

def clear():
    os.system("clear||cls")

def show_game(data: PublicGameData, player: PublicPlayer):
    """Log the current state of the game."""
    def pretty_cards(cards: list[Card] | None):
        if cards is None or len(cards) == 0:
            return ""
        return " ".join([card.ansi_string() for card in cards])

    print()
    print(f"Stage: {str(data.state.game_stage)} | Pot: ${data.state.pot} | Previous Bet: ${data.state.previous_bet}")

    print()
    print(f"Community Cards: {pretty_cards(data.state.community_cards)}")

    print()
    for p in data.players:
        you = ""
        if p == player:
            you = "       <<< YOU"

        if p.folded:
            print(f"{p.name:<15} [FOLDED] {you}")
        else:
            print(f"{p.name:<15} (Bet: ${p.current_bet})   {pretty_cards(p.revealed_pocket_cards)} {you}")

    print()

async def main():
    url: str
    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        url = input("Enter PokerFaceoff server URL: ")

    name = input("What is your name: ")

    self_id: int = -1
    try:
        async with connect(url, ping_interval=5) as ws:
            await send(ws, ClientResponse(action=Join(name=name, disable_time_limit=True)))
            response = await recv(ws)
            match response.action:
                case ServerError(message=message):
                    print(f"Failed to connect to server: {message}")
                    return
                case JoinSuccess(id=id):
                    self_id = id
                    print(f"Successfully joined the server with ID {self_id}")
                case _:
                    print("Unreachable")
                    return

            while True:
                response = await recv(ws)
                match response.action:
                    case ServerError(message=message):
                        print(f"Server error: {message}")
                        return
                    case RoundStarting(data=data):
                        print("Starting round...")
                    case RoundEnd(data=data, winners=winners):
                        clear()
                        names = ", ".join([p.name for p in winners])
                        print(f"Round ended! Winners: {names}")
                        input()
                    case YourTurn(data=data):
                        clear()
                        show_game(data, get_me(data, self_id))
                        print()
                        print("It's your turn!")
                        print("Type in \"fold\" to fold.")
                        print("Type in \"show\" to show your hand (showdown only).")
                        print("Type in a number to bet up to a certain amount (must follow betting rules).")

                        result = None
                        while True:
                            option = input("Input: ")
                            if option.lower() == "fold":
                                result = Fold()
                            elif option.lower() == "show":
                                result = Show()
                            else:
                                try:
                                    bet = int(option)
                                    result = Bet(up_to=bet)
                                except:
                                    print("Invalid input. Try again.")
                                    continue
                            break

                        await send(ws, ClientResponse(action=result))
                    case _:
                        print("Unreachable")
                        return

    except ConnectionClosed:
        pass
    finally:
        pass

if __name__ == "__main__":
    asyncio.run(main())
