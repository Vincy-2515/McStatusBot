from datetime import datetime
import inspect

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def printINFO(message):
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)
    blue = "\033[1;34;34m"
    reset = "\033[0m"
    _, function_name, _ = getCallerInformation()
    print(f"{blue}[{current_time}] [INFO    ] [{function_name}]: {message} {reset}")


def printWARNING(message):
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)
    yellow = "\033[38;5;172m"
    bold = "\033[1m"
    reset = "\033[0m"
    _, function_name, _ = getCallerInformation()
    print(f"{yellow}{bold}[{current_time}] [WARNING ] [{function_name}]: {message} {reset}")


def printERROR(message):
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)
    red = "\033[1;34;31m"
    reset = "\033[0m"
    file_name, function_name, line_number = getCallerInformation()
    print(f"{red}[{current_time}] [ERROR   ] [{file_name}:{line_number}] [{function_name}]:")
    print(f"                        \\------> {message} {reset}")


def getCallerInformation():
    stack_information = inspect.stack()[2]
    file_name = stack_information.filename
    function_name = stack_information.function
    line_number = stack_information.lineno
    return file_name, function_name, line_number
