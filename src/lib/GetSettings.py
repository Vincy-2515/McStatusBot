import tomllib
from typing import Any
import lib.ConsoleMessagesHandling as MSG


class Settings:
    def __init__(self):
        self.bot_token: str
        self.bot_admins: str

        self.is_add_addresses_fields_enabled: bool
        self.server_status_update_delay: int
        self.embed_image_path: str

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
            MSG.printINFO(f"updating settings from '{config_toml_path}'")
        except Exception as e:
            MSG.printERROR(f"could not open '{config_toml_path}': {e}")
            return

        self.bot_token = toml_dict["discord"]["bot_token"]
        self.bot_admins = toml_dict["discord"]["bot_admins"]

        self.is_add_addresses_fields_enabled = toml_dict["discord"]["embed"]["add_addresses_fields"]
        self.server_status_update_delay = toml_dict["discord"]["embed"]["server_status"]["update_delay"]
        self.embed_image_path = toml_dict["discord"]["embed"]["path"]["embed_image"]

        self.server_id = toml_dict["discord"]["id"]["server"]
        self.channel_id = toml_dict["discord"]["id"]["channel"]
        self.message_id = toml_dict["discord"]["id"]["message"]

        self.server_name = toml_dict["minecraft"]["server"]["name"]
        self.server_port = toml_dict["minecraft"]["server"]["port"]
        self.max_players = toml_dict["minecraft"]["server"]["max_players"]
        self.latest_log_path = toml_dict["minecraft"]["server"]["path"]["latest_log"]


if __name__ == "__main__":
    settings = Settings()
    settings.updateSettings("../McStatusBot.toml")
    print(f"bot_token: {settings.bot_token}")
    print(f"bot_admins: {settings.bot_admins}")
    print(f"is_add_addresses_fields_enabled: {settings.is_add_addresses_fields_enabled}")
    print(f"server_status_update_delay: {settings.server_status_update_delay}")
    print(f"embed_image_path: {settings.embed_image_path}")
    print(f"server_id: {settings.server_id}")
    print(f"channel_id: {settings.channel_id}")
    print(f"message_id: {settings.message_id}")
    print(f"server_name: {settings.server_name}")
    print(f"server_port: {settings.server_port}")
    print(f"max_players: {settings.max_players}")
    print(f"latest_log_path: {settings.latest_log_path}")
