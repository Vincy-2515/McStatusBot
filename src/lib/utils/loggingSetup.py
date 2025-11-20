import logging, datetime, os
import lib.globals as GLOBALS

COLOR_TIME = "\033[38;5;59m"
COLOR_LEVEL_NAME = "\033[38;5;25m"
COLOR_NAME = "\033[38;5;105m"
COLOR_MESSAGE = "\033[38;5;59m"
COLOR_RESET = "\033[0m"

LOG_MESSAGE_TIME_FORMAT = "%A, %H:%M:%S"

FILE_LOG_MESSAGE_FORMAT = "[{asctime}][{levelname}][{filename}:{lineno}]: {message}"
CONSOLE_LOG_MESSAGE_FORMAT = (
    "["
    + COLOR_TIME
    + " {asctime} "
    + COLOR_RESET
    + "]"
    + "["
    + COLOR_LEVEL_NAME
    + " {levelname:8} "
    + COLOR_RESET
    + "]"
    + "["
    + COLOR_NAME
    + " {filename:>24.24}:{lineno:<6} "
    + COLOR_RESET
    + "]:"
    + " {message}"
)

LOG_DIRECTORY_PATH = "./logs"

logger: logging.Logger


def loggingSetup():
    global logger
    logger = logging.getLogger(__name__)
    discord_logger = logging.getLogger("discord")
    logging.basicConfig(level=logging.INFO, datefmt=LOG_MESSAGE_TIME_FORMAT, format=CONSOLE_LOG_MESSAGE_FORMAT, style="{")

    logger.info("Press [CTRL]+[C] to stop the bot, enjoy :)")

    try:
        os.makedirs(LOG_DIRECTORY_PATH)
        logger.info(f"Directory '{LOG_DIRECTORY_PATH}' created successfully")
    except FileExistsError:
        # logger.info(f"Directory '{LOG_DIRECTORY_PATH}' already exists")
        pass
    except OSError as e:
        logger.error(f"Error creating/accessing directory '{LOG_DIRECTORY_PATH}': {e}")
        return

    now = datetime.datetime.now()
    logger_file_handler = logging.FileHandler(f"{LOG_DIRECTORY_PATH}/{now.date()}_{now.strftime('%H,%M,%S')}.log")
    logger_file_handler.setLevel(level=logging.INFO)
    logger_file_handler_formatter = logging.Formatter(FILE_LOG_MESSAGE_FORMAT, datefmt=LOG_MESSAGE_TIME_FORMAT, style="{")
    logger_file_handler.setFormatter(logger_file_handler_formatter)

    logger.addHandler(logger_file_handler)
    discord_logger.addHandler(logger_file_handler)


def deleteOldLogs():
    logs_directory_list = os.listdir(LOG_DIRECTORY_PATH)

    while len(logs_directory_list) > GLOBALS.settings.max_number_of_logs_stored:
        logs_directory_list.sort()
        oldest_log = logs_directory_list[0]
        logger.info(f"Removing '{oldest_log}'")
        os.remove(LOG_DIRECTORY_PATH + "" + oldest_log)
        logs_directory_list = os.listdir(LOG_DIRECTORY_PATH)
