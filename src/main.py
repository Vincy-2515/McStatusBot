import sys, logging, argparse
import lib.utils.loggingSetup as LOG
import lib.globals as GLOBALS

logger = logging.getLogger(__name__)

LOG.loggingSetup()

parser = argparse.ArgumentParser()
parser.add_argument("--config-toml", type=str, help="The path to the configuration TOML file.")
args = parser.parse_args()

logger.info(f"Received 'config_toml' path: '{args.config_toml}'")

try:
    GLOBALS.config_toml_path = args.config_toml
    GLOBALS.settings.updateSettings(GLOBALS.config_toml_path)
except Exception as e:
    logger.critical(f"failed the collection of the settings from the file: {e}")
    sys.exit(1)

import lib.bot.bot as BOT

BOT.run()

