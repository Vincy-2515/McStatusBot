import tomli
BOT_VALUES_FILE = "Parrot_BOT_settings.txt"

class Settings:
    def __init__(self):
        self.bot_token:str
        self.server_id:int
        self.channel_id:int
        self.server_status_message_id:int
        self.addresses_message_id:int
        self.updateServerStatusEmbed_task_delay:int
        self.max_players:int
        self.latest_log_path:str

    def updateValues (self):
        self.bot_token = self.getValueFromFile ("bot_token")
        self.server_id = int(self.getValueFromFile ("server_id"))
        self.channel_id = int(self.getValueFromFile ("channel_id"))
        self.server_status_message_id = int(self.getValueFromFile ("server_status_message_id"))
        self.addresses_message_id = int(self.getValueFromFile ("addresses_message_id"))
        self.updateServerStatusEmbed_task_delay = int(self.getValueFromFile ("updateServerStatusEmbed_task_delay"))
        self.max_players = int(self.getValueFromFile ("max_players"))
        self.latest_log_path = self.getValueFromFile ("latest_log_path")

    def getValueFromFile (self, value_to_find):
        i: int = 0

        file = open(BOT_VALUES_FILE, 'r')
        lines = file.readlines()
        file.close()

        while i < len(lines):
            if (lines[i].find(value_to_find) != -1):
                value_to_find = lines[i].split()
                break
            i += 1

        return value_to_find[1]

if __name__ == '__main__':
    values = Settings()
    values.updateValues()
    print(values.bot_token)
    print(values.server_id)
    print(values.channel_id)
    print(values.server_status_message_id)
    print(values.addresses_message_id)
    print(values.updateServerStatusEmbed_task_delay)
    print(values.max_players)
    print(values.latest_log_path)
