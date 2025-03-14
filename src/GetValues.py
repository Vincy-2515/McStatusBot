import tomllib
from resources import ConsoleMessagesHandling as MSG

BOT_TOML = "Parrot_BOT.toml"


class Settings:
    def __init__(self):
        self.bot_token: str
        self.path_embed_image: str
        self.update_delay_serverStatus: int
        self.update_delay_serverStatusEmbed: int
        self.id_server: int
        self.id_channel: int
        self.id_message_serverStatus: int
        self.max_players: int
        self.path_latest_log: str
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
        self.path_embed_image = toml_dict["discord"]["path"]["embed_image"]
        self.update_delay_serverStatus = toml_dict["discord"]["update_delay"]["serverStatus"]
        self.update_delay_serverStatusEmbed = toml_dict["discord"]["update_delay"]["serverStatusEmbed"]
        self.id_server = toml_dict["discord"]["id"]["server"]
        self.id_channel = toml_dict["discord"]["id"]["channel"]
        self.id_message_serverStatus = toml_dict["discord"]["id"]["message"]["server_status"]
        self.max_players = toml_dict["minecraft"]["max_players"]
        self.path_latest_log = toml_dict["minecraft"]["path"]["latest_log"]


if __name__ == "__main__":
    values = Settings()
    print(values.bot_token)
    print(values.path_embed_image)
    print(values.update_delay_serverStatus)
    print(values.update_delay_serverStatusEmbed)
    print(values.id_server)
    print(values.id_channel)
    print(values.id_message_serverStatus)
    print(values.max_players)
    print(values.path_latest_log)
