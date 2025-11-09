from datetime import datetime
import inspect

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_FUNCTION_NAME_LENGTH = 32


def printINFO(message: str):
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)

    blue = "\033[1;34;34m"
    reset = "\033[0m"

    _, function_name, _ = getCallerInformation()
    function_name = formatFunctionName(function_name, MAX_FUNCTION_NAME_LENGTH)
    print(f"{blue}[{current_time}] [INFO    ] [{function_name}]: {message} {reset}")


def printWARNING(message: str):
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)

    yellow = "\033[38;5;172m"
    bold = "\033[1m"
    reset = "\033[0m"

    _, function_name, _ = getCallerInformation()
    function_name = formatFunctionName(function_name, MAX_FUNCTION_NAME_LENGTH)
    print(f"{yellow}{bold}[{current_time}] [WARNING ] [{function_name}]: {message} {reset}")


def printERROR(message: str):
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


def formatFunctionName(function_name: str, max_function_name_length: int, ellipsis: str = "..."):
    function_name_length = len(function_name)
    formatted_function_name = ""
    i = 0

    if function_name_length < max_function_name_length:
        while i < (max_function_name_length - function_name_length):
            formatted_function_name += " "
            i += 1
        formatted_function_name += function_name

    elif function_name_length == max_function_name_length:
        formatted_function_name = function_name

    elif function_name_length > max_function_name_length:
        formatted_function_name = function_name[: max(0, max_function_name_length - len(ellipsis))] + ellipsis

    return formatted_function_name
