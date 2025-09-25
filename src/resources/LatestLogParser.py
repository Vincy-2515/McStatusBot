import resources.ConsoleMessagesHandling as MSG

STRING_SERVER_STATUS_STARTING = ":yellow_circle: Starting..."
STRING_SERVER_STATUS_ONLINE = ":green_circle: Online"
STRING_SERVER_STATUS_OFFLINE = ":red_circle: Offline"


def parseLatestLogForServerStatus(path: str) -> str:
    i: int = 0
    server_status: str = ""

    file = open(path, "r")
    lines = file.readlines()
    file.close()

    while i < len(lines):
        if (lines[i].find("[Server thread/INFO]") != -1) and (lines[i].find("Stopping the server") != -1):
            server_status = STRING_SERVER_STATUS_OFFLINE
            break
        elif (lines[i].find("[Server thread/INFO]") != -1) and (lines[i].find('For help, type "help"') != -1):
            server_status = STRING_SERVER_STATUS_ONLINE
        elif lines[i].find("[main/INFO]: Loading Minecraft") != -1:
            server_status = STRING_SERVER_STATUS_STARTING

        i += 1

    if server_status == "":
        MSG.printERROR("failed to obtain the server status")
        return ":red_circle: Offline"

    return server_status


def parseLatestLogForPlayerCount(path: str) -> int:
    i: int = 0
    player_count: int = 0

    file = open(path, "r")
    lines = file.readlines()
    file.close()

    while i < len(lines):
        if lines[i].find("[Server thread/INFO]") != -1:
            if lines[i].find("joined the game") != -1:
                player_count += 1
            elif lines[i].find("left the game") != -1:
                player_count -= 1
        i += 1

        if player_count < 0:
            player_count = 0

    return player_count


if __name__ == "__main__":
    path = "src\\resources\\mc-logs\\latest.log"
    server_status = parseLatestLogForServerStatus(path)
    player_count = parseLatestLogForPlayerCount(path)
    print(f"Server status: {server_status}")
    print(f"Players: {player_count}")
