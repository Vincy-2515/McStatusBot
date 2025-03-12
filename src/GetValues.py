import tomllib
from resources import ConsoleMessagesHandling as MSG

BOT_TOML = "Parrot_BOT.toml"


class Settings:
    def __init__(self):
        self.server_id: int
        self.channel_id: int
        self.server_status_message_id: int
        self.addresses_message_id: int
        self.server_status_update_delay: int
        self.bot_token: str
        self.max_players: int
        self.latest_log_path: str

    def updateValues(self):
        try:
            file = open(BOT_TOML, "rb")
            toml_dict: dict = tomllib.load(file)
        except Exception as e:
            MSG.printERROR(f"could not open {BOT_TOML}: {e}")
            return

        self.server_id = toml_dict["discord"]["id"]["server"]
        self.channel_id = toml_dict["discord"]["id"]["channel"]
        self.server_status_message_id = toml_dict["discord"]["id"]["message"]["server_status"]
        self.addresses_message_id = toml_dict["discord"]["id"]["message"]["addresses"]
        self.server_status_update_delay = toml_dict["discord"]["server_status_update_delay"]
        self.bot_token = toml_dict["discord"]["bot_token"]

        self.max_players = toml_dict["minecraft"]["max_players"]
        self.latest_log_path = toml_dict["minecraft"]["path"]["latest_log"]


if __name__ == "__main__":
    values = Settings()
    values.updateValues()
    print(values.server_id)
    print(values.channel_id)
    print(values.server_status_message_id)
    print(values.addresses_message_id)
    print(values.server_status_update_delay)
    print(values.bot_token)
    print(values.max_players)
    print(values.latest_log_path)
