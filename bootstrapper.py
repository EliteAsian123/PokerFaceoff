import asyncio
import subprocess
import sys
import platform
import server.main

def main():
    print()
    print("                  ==== Welcome to the PokerFaceoff Bootstrapper ====")
    print("The bootstrapper will start an instance of the server, and any number client instances.")
    print("To begin, type the name of the Python module within this project that contains the client")
    print("instance you want to start. Repeat this until you have enough players, and then press enter")
    print("on an empty line to begin. You can also use a semi-colon followed by a number to start multiple")
    print("instances.")
    print()
    print("For example: client.template.main;4")
    print()

    modules: list[str] = []
    while True:
        m = input("> ")
        if len(m) == 0:
            break

        if ";" in m:
            index = m.index(";")
            module = m[:index]
            number = int(m[(index + 1):])
            for _ in range(number):
                modules.append(module)
        else:
            modules.append(m)

    for module in modules:
        open_client_instance(module)

    print("All instances have started. Switching to server...")
    asyncio.run(server.main.main(len(modules)))

def open_client_instance(module_name: str):
    ARG = "ws://localhost:8001"

    current_os = platform.system()
    match current_os:
        case "Windows":
            # 'start' is a Windows command; /k keeps the window open after the script finishes
            subprocess.Popen(
                ["start", "cmd", "/k", sys.executable, "-m", module_name, ARG],
                shell=True
            )
        case "Darwin":
            # Uses AppleScript via osascript to open a new Terminal window
            cmd = f"python3 -m {module_name} {ARG}"
            subprocess.Popen(
                ["osascript", "-e", f'tell application "Terminal" to do script "{cmd}"']
            )
        case "Linux":
            # Tries gnome-terminal first, falls back to xterm if needed
            try:
                subprocess.Popen(
                    ["gnome-terminal", "--", sys.executable, "-m", module_name, ARG]
                )
            except FileNotFoundError:
                subprocess.Popen(
                    ["xterm", "-e", f"{sys.executable} -m {module_name} {ARG}"]
                )
        case _:
            raise ValueError("Unable to start client instance on this platform.")

if __name__ == "__main__":
    main()
