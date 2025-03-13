from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def printINFO(message):
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)
    blue = "\033[1;34;34m"
    reset = "\033[0m"
    print(f"{blue}[{current_time}] [INFO    ]: {message} {reset}")


def printWARNING(message):
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)
    yellow = "\033[38;5;172m"
    bold = "\033[1m"
    reset = "\033[0m"
    print(f"{yellow}{bold}[{current_time}] [WARNING ]: {message} {reset}")


def printERROR(message):
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)
    red = "\033[1;34;31m"
    reset = "\033[0m"
    print(f"{red}[{current_time}] [ERROR   ]: {message} {reset}")
