ENABLE_LOGGING = True

def log(s: str | None = None):
    if ENABLE_LOGGING:
        if s == None:
            print()
        else:
            print(s)

def log_server_action(s: str):
    log(f"\033[34m>\033[0m {s}")

def log_client_action(s: str):
    log(f"\033[32m<\033[0m {s}")
