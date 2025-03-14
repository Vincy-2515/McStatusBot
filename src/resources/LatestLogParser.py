import resources.ConsoleMessagesHandling as MSG


def parseLatestLogForServerStatus(path: str) -> str:
    i: int = 0
    server_status: str = ""

    file = open(path, "r")
    lines = file.readlines()
    file.close()

    while i < len(lines):
        if lines[i].find("[Server thread/INFO]") != -1:
            if lines[i].find('For help, type "help"') != -1:
                server_status = "🟢 Online"
            elif lines[i].find("Stopping the server") != -1:
                server_status = "🔴 Offline"
                break
        i += 1

    if server_status == "":
        MSG.printERROR("failed to obtain the server status")
        return "🔴 Offline"

    MSG.printINFO("successfully obtained the server status")
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
                break
        i += 1

    MSG.printINFO("obtained the current player count")

    return player_count


def parseLatestLogForE4MCAddress(path: str) -> str:
    splitted_current_line: str = ""
    e4mc_address: str = ""

    file = open(path, "r")
    lines = file.readlines()
    file.close()

    i = 0
    while i < len(lines):
        if lines[i].find("[nioEventLoopGroup-2-1/INFO]: Domain assigned:") != -1:
            splitted_current_line = lines[i].split()
            break

        i += 1

    e4mc_address = splitted_current_line[4]

    if e4mc_address == "":
        MSG.printERROR("Failed to obtain the e4mc address")
        return "-- non disponibile --"

    MSG.printINFO("Successfully obtained the e4mc address")

    return e4mc_address


if __name__ == "__main__":
    path = "src\\resources\\logs\\latest.log"
    server_status = parseLatestLogForServerStatus(path)
    player_count = parseLatestLogForPlayerCount(path)
    e4mc_address = parseLatestLogForE4MCAddress(path)
    print(f"Srver Online?: {server_status}")
    print(f"Players: {player_count}")
    print(f"e4mc_address: {e4mc_address}")
