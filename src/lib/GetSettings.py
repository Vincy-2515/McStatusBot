import tomllib, logging, os
from typing import Any

logger = logging.getLogger(__name__)


class Settings:
    def __init__(self):
        self.max_number_of_logs_stored: int

        self.bot_token: str
        self.bot_admins: str

        self.server_status_update_delay: int
        self.embed_image_path: str

        self.is_add_addresses_fields_enabled: bool
        self.network_cards: list[str]
        self.is_show_e4mc_address_enabled: bool

        self.server_id: int
        self.channel_id: int
        self.message_id: int

        self.server_name: str
        self.server_port: int
        self.max_players: int
        self.latest_log_path: str

    def updateSettings(self, config_toml_path: str):
        try:
            file = open(config_toml_path, "rb")
            toml_dict: dict[str, Any] = tomllib.load(file)
            file.close()
            logger.info(f"Updating settings from '{config_toml_path}'")
        except Exception as e:
            raise Exception(f"could not open '{config_toml_path}': {e}")

        self.__getSettingsFromFile(toml_dict)

        try:
            self.__validateSettings()
        except Exception as e:
            raise Exception(f"Settings validation failed, fix configuration and restart: {e}")

    def __getSettingsFromFile(self, toml_dict: dict[str, Any]):
        self.max_number_of_logs_stored = toml_dict["app"]["max_number_of_logs_stored"]

        self.bot_token = toml_dict["discord"]["bot"]["token"]
        self.bot_admins = toml_dict["discord"]["bot"]["admins"]

        self.server_status_update_delay = toml_dict["discord"]["embed"]["server_status"]["update_delay"]
        self.embed_image_path = toml_dict["discord"]["embed"]["path"]["embed_image"]

        self.is_add_addresses_fields_enabled = toml_dict["discord"]["embed"]["connectivity"]["add_addresses_fields"]
        self.network_cards = toml_dict["discord"]["embed"]["connectivity"]["network_cards"]
        self.is_show_e4mc_address_enabled = toml_dict["discord"]["embed"]["connectivity"]["show_e4mc_address"]

        self.server_id = toml_dict["discord"]["id"]["server"]
        self.channel_id = toml_dict["discord"]["id"]["channel"]
        self.message_id = toml_dict["discord"]["id"]["message"]

        self.server_name = toml_dict["minecraft"]["server"]["name"]
        self.server_port = toml_dict["minecraft"]["server"]["port"]
        self.max_players = toml_dict["minecraft"]["server"]["max_players"]
        self.latest_log_path = toml_dict["minecraft"]["server"]["path"]["latest_log"]


    def __validateSettings(self):
        if self.max_number_of_logs_stored < 1:
            raise Exception("The minimum number of logs is 1")

        if self.bot_token == "":
            raise Exception("'bot_token' must be provided")

        if len(self.bot_admins) == 0:
            raise Exception("There should be at least one bot admin")

        if self.server_status_update_delay < 1:
            raise Exception("Invalid value for 'server_status_update_delay'")

        if not os.path.isfile(self.embed_image_path):
            raise Exception("Invalid path: 'embed_image_path'")

        if not self.is_add_addresses_fields_enabled and (len(self.network_cards) != 0):
            raise Exception("'is_add_addresses_fields_enabled' is set to False but 'network_cards' has some values")

        if not self.is_add_addresses_fields_enabled and (self.is_show_e4mc_address_enabled != False):
            raise Exception("'is_add_addresses_fields_enabled' is set to False but 'is_show_e4mc_address_enabled' is True")

        # TODO: add discord ids validation (server, channel, message)

        if self.server_name == "":
            raise Exception("A value must be provided for 'server_name'")

        if self.max_players < 1:
            raise Exception("Invalid value for 'max_players'")

        if not os.path.isfile(self.latest_log_path):
            raise Exception("Invalid path: 'latest_log_path'")


if __name__ == "__main__":
    settings = Settings()
    settings.updateSettings("../McStatusBot.toml")
    print(f"maximum_number_of_logs_stored: {settings.max_number_of_logs_stored}")
    print(f"bot_token: {settings.bot_token}")
    print(f"bot_admins: {settings.bot_admins}")
    print(f"server_status_update_delay: {settings.server_status_update_delay}")
    print(f"embed_image_path: {settings.embed_image_path}")
    print(f"is_add_addresses_fields_enabled: {settings.is_add_addresses_fields_enabled}")
    print(f"network_cards: {settings.network_cards}")
    print(f"is_show_e4mc_address_enabled: {settings.is_show_e4mc_address_enabled}")
    print(f"server_id: {settings.server_id}")
    print(f"channel_id: {settings.channel_id}")
    print(f"message_id: {settings.message_id}")
    print(f"server_name: {settings.server_name}")
    print(f"server_port: {settings.server_port}")
    print(f"max_players: {settings.max_players}")
    print(f"latest_log_path: {settings.latest_log_path}")
