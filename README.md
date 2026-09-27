# PokerFaceoff

A simple Python framework to build Texas Hold'em Poker bots, and a server to face them off against each other. It includes a WebSocket game server, a bot template for writing your own clients, a "manual" client for playing as a human, and a bootstrapper that launches many client instances in separate terminal windows at once.

## Features

* Server: an async (WebSocket) Texas Hold'em game server with a lobby and continuous round loop.
* Bot template: drop-in starting point for writing and running your own poker bot.
* Manual client: play as a human from the console.
* Bootstrapper: one command to start a server plus any number of client instances in new terminal windows.

## Requirements

Python 3.10+ is required. Additionally, the following dependencies are needed:
```bash
pip install websockets pydantic
```

## Running the Server

From the repo root:
```bash
python -m server.main <expected_player_count>
```
For example, use `python -m server.main 3` for a 3-player table.

The server binds to `ws://localhost:8001`.

## Running Clients

Both clients take an optional server URL as the first argument; if omitted, they prompt for it (default in both cases is `ws://localhost:8001`):

```bash
# Run the template bot (folds everything by default)
python -m client.template.main [server-url]

# Play as a human
python -m client.manual.main [server-url]
```

## The Bootstrapper

The bootstrapper starts the server and any number of clients, each in its own terminal window:

```bash
python -m bootstrapper
```

It prompts you for Python module names, one per line (e.g. `client.template.main`, `client.manual.main`, or your own):
```
> client.manual.main
> client.template.main
> client.template.main;4     # starts 4 instances of that module
>                            # empty line starts the game
```

## Writing Your Own Bot

1. Copy the `client/template/` directory (e.g. `client/mybot/`).
2. Put your logic in `client/mybot/bot.py`. `client/mybot/main.py` contains server connection stuff that you shouldn't have to worry about.
3. Run it with `python -m client.mybot.main`, or launch it with the bootstrapper.

TODO: Write about the main `bot.py` functions.

Available actions returned from `action(...)`:

| Action            | Notes |
|-------------------|-------|
| `Fold()`          | Always valid |
| `Show()`          | Only valid during showdown |
| `Bet(up_to=N)`    | Check/call /raise, all through one action (see rules below) |
| `AllIn()`         | TODO |

Betting rules enforced by the server (per action, on your turn):
* `up_to < current bet` -> illegal.
* `up_to == current bet` -> checked.
* `up_to == previous bet` -> called.
* `up_to > previous bet` but less than `2 * previous bet` -> illegal (re-raises must double the current bet).
* `up_to >= 2 * previous bet` -> raised.

Any illegal action results in an instant fold. Additionally, if a bot fails to answer within 10 seconds, it is treated as folding.

## License

This project is under the MIT (see [LICENSE.md](LICENSE.md)).
