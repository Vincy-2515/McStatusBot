import tomllib
from resources import ConsoleMessagesHandling as MSG

BOT_TOML = "Parrot_BOT.toml"


class Settings:
    def __init__(self):
        self.bot_token: str
        self.serverStatus_update_delay: int
        self.id_server: int
        self.id_channel: int
        self.id_message_serverStatus: int
        self.id_message_addresses: int
        self.path_embed_image: str
        self.max_players: int
        self.path_latest_log: str

    def updateValues(self):
        try:
            file = open(BOT_TOML, "rb")
            toml_dict: dict = tomllib.load(file)
        except Exception as e:
            MSG.printERROR(f"could not open {BOT_TOML}: {e}")
            return

        self.bot_token = toml_dict["discord"]["bot_token"]
        self.serverStatus_update_delay = toml_dict["discord"]["serverStatus_update_delay"]
        self.id_server = toml_dict["discord"]["id"]["server"]
        self.id_channel = toml_dict["discord"]["id"]["channel"]
        self.id_message_serverStatus = toml_dict["discord"]["id"]["message"]["server_status"]
        self.id_message_addresses = toml_dict["discord"]["id"]["message"]["addresses"]
        self.path_embed_image = toml_dict["discord"]["path"]["embed_image"]
        self.max_players = toml_dict["minecraft"]["max_players"]
        self.path_latest_log = toml_dict["minecraft"]["path"]["latest_log"]


if __name__ == "__main__":
    values = Settings()
    values.updateValues()
    print(values.bot_token)
    print(values.serverStatus_update_delay)
    print(values.id_server)
    print(values.id_channel)
    print(values.id_message_serverStatus)
    print(values.id_message_addresses)
    print(values.path_embed_image)
    print(values.max_players)
    print(values.path_latest_log)
