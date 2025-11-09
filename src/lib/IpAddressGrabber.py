import subprocess
import lib.ConsoleMessagesHandling as MSG


def ipAddressGrabber(net_card: str):
    ip_address = ""
    command = f"Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias '{net_card}'"
    stdout = subprocess.run(["powershell", "-Command", command], capture_output=True)

    if stdout.returncode != 0:
        MSG.printWARNING(f'"Get-NetIPAddress" failed for "{net_card}", skipping')
        return ""
    else:
        MSG.printINFO(f'"Get-NetIPAddress" successful for "{net_card}"')
        decoded_stdout = stdout.stdout.decode()

    splitted_stdout = decoded_stdout.split()

    i = 0
    for string in splitted_stdout:
        if string.find("IPAddress") != -1:
            ip_address = splitted_stdout[i + 2]
        else:
            i += 1
            continue

    if ip_address == "":
        MSG.printERROR(f'Failed to obtain {net_card} address from the "Get-NetIPAddress" output')
        return ""
    else:
        MSG.printINFO(f'Successfully obtained {net_card} address from the "Get-NetIPAddress" output')
        return ip_address


if __name__ == "__main__":
    print(f'Ethernet IPv4: {ipAddressGrabber("Ethernet")}')
    print(f'Hamachi IPv4: {ipAddressGrabber("Hamachi")}')
