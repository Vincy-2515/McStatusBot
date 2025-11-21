import sys, logging, argparse
import lib.utils.loggingSetup as Log
import lib.globals as Globals

root_logger = logging.getLogger()

def main():
    Log.loggingSetup(root_logger)

    parser = argparse.ArgumentParser()
    parser.add_argument("--config-toml", type=str, help="The path to the configuration TOML file.")
    args = parser.parse_args()

    root_logger.info(f"Received 'config_toml' path: '{args.config_toml}'")

    try:
        if args.config_toml is None:
            args.config_toml = "McStatusBot.toml"
        Globals.config_toml_path = args.config_toml
        Globals.settings.updateSettings(Globals.config_toml_path)
    except Exception as e:
        root_logger.critical(f"failed the collection of the settings from the file: {e}")
        sys.exit(1)

    Log.deleteOldLogs(root_logger)

    import lib.bot.bot as bot
    bot.run()

main()