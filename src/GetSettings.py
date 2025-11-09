import tomllib
from resources import ConsoleMessagesHandling as MSG

BOT_TOML = "Reworked_BOT.toml"


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

        self.max_players: int
        self.server_port: int
        self.latest_log_path: str

        self.updateSettings()

    def updateSettings(self):
        try:
            file = open(BOT_TOML, "rb")
            toml_dict: dict = tomllib.load(file)
            MSG.printINFO(f"updating settings from {BOT_TOML}")
        except Exception as e:
            MSG.printERROR(f"could not open {BOT_TOML}: {e}")
            return

        self.bot_token = toml_dict["discord"]["bot_token"]
        self.bot_admins = toml_dict["discord"]["bot_admins"]

        self.is_add_addresses_fields_enabled = toml_dict["discord"]["embed"]["add_addresses_fields"]
        self.server_status_update_delay = toml_dict["discord"]["embed"]["server_status"]["update_delay"]
        self.embed_image_path = toml_dict["discord"]["embed"]["path"]["embed_image"]

        self.server_id = toml_dict["discord"]["id"]["server"]
        self.channel_id = toml_dict["discord"]["id"]["channel"]
        self.message_id = toml_dict["discord"]["id"]["message"]

        self.max_players = toml_dict["minecraft"]["max_players"]
        self.server_port = toml_dict["minecraft"]["server_port"]
        self.latest_log_path = toml_dict["minecraft"]["path"]["latest_log"]


if __name__ == "__main__":
    settings = Settings()
    print(settings.bot_token)
    print(settings.bot_admins)
    print(settings.is_add_addresses_fields_enabled)
    print(settings.server_status_update_delay)
    print(settings.embed_image_path)
    print(settings.server_id)
    print(settings.channel_id)
    print(settings.message_id)
    print(settings.max_players)
    print(settings.server_port)
    print(settings.latest_log_path)
