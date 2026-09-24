ENABLE_LOGGING = True

def log(s: str | None = None):
    if ENABLE_LOGGING:
        if s is None:
            print()
        else:
            print(s)

def log_important(s: str):
    print(f"\033[31m{s}\033[0m")

def log_server_action(s: str):
    log(f"\033[34m>\033[0m {s}")

def log_client_action(s: str):
    log(f"\033[32m<\033[0m {s}")
