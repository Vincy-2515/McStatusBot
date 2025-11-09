import time
import datetime
import sys
import discord
from typing import Any, Optional
import argparse
from discord.ext import commands
from discord.ext import tasks
import lib.GetSettings as SETTINGS
import lib.LatestLogParser as MCLOG
import lib.ConsoleMessagesHandling as MSG
import lib.IpAddressGrabber as IPADDRESS

config_toml_path: str = ""
settings = SETTINGS.Settings()
guild_id: discord.Object


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-toml", type=str, help="The path to the configuration TOML file.")
    args = parser.parse_args()

    MSG.printINFO(f"Received 'config_toml' path: '{args.config_toml}'")

    try:
        global config_toml_path, settings, guild_id
        config_toml_path = args.config_toml
        settings.updateSettings(config_toml_path)
        guild_id = discord.Object(id=settings.server_id)
    except Exception as e:
        MSG.printERROR(f"failed the collection of the settings from the file: {e}")


main()  # MUST BE CALLED BEFORE THE DEFINITION OF EVERYTHING ELSE


class Client(commands.Bot):
    def __init__(self, *args: tuple[Any], **kwargs: dict[str, Any]):
        super().__init__(*args, **kwargs)
        self.startup_time: datetime.datetime
        self.after_online: bool = False

        self.player_count: int = 0
        self.server_status: str = ""
        self.previous_player_count: int = 0
        self.previous_server_status: str = ""
        self.cycles_count = 0

        self.ethernet_address: str = ""
        self.wifi_address: str = ""
        self.hamachi_address: str = ""
        self.e4mc_address: str = ""

    async def on_ready(self):
        if client.user is None:
            MSG.printERROR("The bot user is not initialized.")
            return

        MSG.printINFO(f"logged in as {client.user} (ID: {client.user.id})")
        MSG.printWARNING("press [CTRL]+[C] to stop the bot, enjoy :)")

        try:
            synced = await self.tree.sync(guild=guild_id)
            MSG.printINFO(f"synchronized {len(synced)} command(s)")
        except Exception as e:
            MSG.printERROR(f"commands synchronization error: {e}")

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=guild_id)
        self.updateServerStatus.start()

    @tasks.loop(seconds=settings.server_status_update_delay)
    async def updateServerStatus(self):
        self.server_status = MCLOG.parseLatestLogForServerStatus(settings.latest_log_path)
        self.player_count = MCLOG.parseLatestLogForPlayerCount(settings.latest_log_path)

        if (self.previous_player_count != self.player_count) or (self.previous_server_status != self.server_status):
            MSG.printINFO(
                f"Values have changed after {self.cycles_count} cycles (or {self.cycles_count * settings.server_status_update_delay} seconds)"
            )

            if self.server_status == MCLOG.STRING_SERVER_STATUS_ONLINE and self.after_online == False:
                MSG.printINFO("The server is online")

                if settings.is_add_addresses_fields_enabled:
                    updateAddresses()

                self.startup_time = datetime.datetime.now()
                self.after_online = True

            elif self.server_status == MCLOG.STRING_SERVER_STATUS_STARTING:
                MSG.printINFO("The server is starting")

            elif self.server_status == MCLOG.STRING_SERVER_STATUS_OFFLINE and self.after_online == True:
                MSG.printINFO("The server is offline, starting shutdown procedure...")
                await shutdown(forced_shutdown=False)

            await updateServerStatusEmbed()
            updatePreviousValues()

        else:
            self.cycles_count += 1

    @updateServerStatus.before_loop
    async def beforeUpdateServerStatus(self):
        await self.wait_until_ready()


intents = discord.Intents.default()

intents = {"guild_messages": True, "message_content": True, "expressions": True}
client = Client(intents=intents)

### commands ##############################################################################


@client.tree.command(
    name="sendstatus", description="Invia un embed contenente lo stato del server e gli indirizzi per la connessione ad esso"
)
async def sendstatus(interaction: discord.Interaction):
    if await handleCommandInvocation(interaction=interaction, command_name="sendstatus", admin_only_command=True) == False:
        return

    await interaction.response.defer(thinking=True)

    image, server_status_embed = getServerStatusEmbed()
    previous_message = await getMessage(settings.channel_id, settings.message_id)

    if not isinstance(previous_message, discord.Message):
        MSG.printERROR(f"The message {settings.message_id} is not a Message")
        return

    try:
        await previous_message.edit()
        await interaction.followup.send("Ho modificato il messaggio già esistente")
    except Exception as e:
        MSG.printWARNING(f"couldn't edit the server stauts message, sending a new message. Error: {e}")
        await interaction.followup.send(file=image, embed=server_status_embed)
        settings.updateSettings(config_toml_path)


@client.tree.command(name="reloaddata", description="Ricarica tutti i dati che il bot raccoglie da vari files")
async def reloaddata(interaction: discord.Interaction):
    if await handleCommandInvocation(interaction=interaction, command_name="reloaddata", admin_only_command=True) == False:
        return

    await interaction.response.defer(thinking=True)

    try:
        settings.updateSettings(config_toml_path)

        if settings.is_add_addresses_fields_enabled:
            updateAddresses()

        client.server_status = MCLOG.parseLatestLogForServerStatus(settings.latest_log_path)
        client.player_count = MCLOG.parseLatestLogForPlayerCount(settings.latest_log_path)

        await updateServerStatusEmbed()

        MSG.printINFO("All data and settings are reloaded")
        await interaction.followup.send("Dati e impostazioni ricaricati")
    except Exception as e:
        MSG.printERROR(f"Reloading failed: {e}")
        await interaction.followup.send("Errore nel ricaricamento, controlla la console per ulteriori informazioni")


@client.tree.command(name="shutdownbot", description="Manda il bot offline")
async def shutdownbot(interaction: discord.Interaction):
    if await handleCommandInvocation(interaction=interaction, command_name="shutdownbot", admin_only_command=True) == False:
        return

    await interaction.response.send_message("Sto per andare offline")
    await shutdown(forced_shutdown=True)


### other functions #######################################################################


async def updateServerStatusEmbed(forced_shutdown: bool = False):
    MSG.printINFO('Updating "server_status_embed"...')
    updateServerStatusEmbed_start_time = time.perf_counter()

    image = None
    server_status_embed = None

    try:
        previous_message = await getMessage(settings.channel_id, settings.message_id)
        image, server_status_embed = getServerStatusEmbed(forced_shutdown=forced_shutdown)

        if not isinstance(previous_message, discord.Message):
            MSG.printERROR(f"The message {settings.message_id} is not a Message")
            return

        await previous_message.edit(
            attachments=[image], embed=server_status_embed
        )  ################################### TROPPO CONSUMO DI TEMPO
    except Exception as e:
        settings.updateSettings(config_toml_path)
        MSG.printERROR(f'failed "server_status_embed" update: {e}')
        MSG.printINFO("sending a new message")
        channel = client.get_channel(settings.channel_id)

        if isinstance(channel, discord.TextChannel):
            if image is not None and server_status_embed is not None:
                await channel.send(file=image, embed=server_status_embed)

    updateServerStatusEmbed_finish_time = time.perf_counter()
    MSG.printINFO(
        f'It took {(updateServerStatusEmbed_finish_time - updateServerStatusEmbed_start_time):.2f} seconds to update "server_status_embed"'
    )
    MSG.printINFO(f'server_status: "{client.server_status}", player_count: {client.player_count}')


async def getMessage(channel_id: int, message_id: int) -> Optional[discord.Message]:
    channel = client.get_channel(channel_id)

    if not isinstance(channel, discord.TextChannel):
        MSG.printERROR(f"The channel {channel_id} is not a TextChannel")
        return

    try:
        try:
            return await channel.fetch_message(message_id)
        except Exception as e:
            MSG.printERROR(f"Unable to fetch the message: {e}")
    except Exception as e:
        MSG.printERROR(f'Error with "id_channel": {e}')
        return None

    return None


def getServerStatusEmbed(forced_shutdown: bool = False) -> tuple[discord.File, discord.Embed]:
    splitted_path = settings.embed_image_path.split("/")
    imagename = splitted_path[len(splitted_path) - 1]
    image = discord.File(settings.embed_image_path, filename=imagename)

    server_status_embed = discord.Embed(title=settings.server_name, colour=discord.Color.dark_gray())

    if client.server_status == MCLOG.STRING_SERVER_STATUS_OFFLINE:
        server_status_embed = discord.Embed(
            title=settings.server_name, colour=discord.Color.red(), timestamp=client.startup_time
        )
    elif client.server_status == MCLOG.STRING_SERVER_STATUS_ONLINE:
        server_status_embed = discord.Embed(
            title=settings.server_name, colour=discord.Color.green(), timestamp=client.startup_time
        )
    elif client.server_status == MCLOG.STRING_SERVER_STATUS_STARTING:
        server_status_embed = discord.Embed(
            title=settings.server_name, colour=discord.Color.yellow(), timestamp=client.startup_time
        )

    addServerStatusFields(server_status_embed)
    if settings.is_add_addresses_fields_enabled:
        addAddressesFields(server_status_embed)

    if forced_shutdown:
        server_status_embed.add_field(
            name="", value=":warning: Lo stato del server potrebbe non essere aggiornato", inline=False
        )

    server_status_embed.set_image(url=f"attachment://{imagename}")

    return image, server_status_embed


async def handleCommandInvocation(interaction: discord.Interaction, command_name: str, admin_only_command: bool) -> bool:
    MSG.printINFO(f'"/{command_name}" invoked by {interaction.user}')

    if (str(interaction.user) not in settings.bot_admins) and (admin_only_command == True):
        await interaction.response.send_message("Non puoi eseguire questo comando")
        return False
    return True


def updatePreviousValues():
    client.previous_player_count = client.player_count
    client.previous_server_status = client.server_status
    client.cycles_count = 0


def addServerStatusFields(server_status_embed: discord.Embed):
    server_status_embed.add_field(name="Server Status:", value=client.server_status)
    if client.server_status == MCLOG.STRING_SERVER_STATUS_OFFLINE:
        server_status_embed.add_field(name="Players online:", value=f"<:steve:1382831305221472468> 0/{settings.max_players}")
    else:
        server_status_embed.add_field(
            name="Players online:", value=f"<:steve:1382831305221472468> {client.player_count}/{settings.max_players}"
        )


def addAddressesFields(server_status_embed: discord.Embed):
    if client.ethernet_address != "" or client.wifi_address != "" or client.e4mc_address != "" or client.hamachi_address != "":
        server_status_embed.add_field(name="Indirizzi per la connessione:", value="", inline=False)

    if client.ethernet_address != "" and client.wifi_address == "":
        server_status_embed.add_field(
            name="",
            value=f"* __Indirizzo locale:__||```{client.ethernet_address}:{settings.server_port}```||",
            inline=False,
        )
    if client.wifi_address != "":
        server_status_embed.add_field(
            name="",
            value=f"* __Indirizzo locale:__||```{client.wifi_address}:{settings.server_port}```||",
            inline=False,
        )
    if client.e4mc_address != "":
        server_status_embed.add_field(
            name="",
            value=f"* __Indirizzo e4mc:__||```{client.e4mc_address}```||",
            inline=False,
        )
    if client.hamachi_address != "":
        server_status_embed.add_field(
            name="",
            value=f"* __Indirizzo Hamachi:__||```{client.hamachi_address}:{settings.server_port}```||",
            inline=False,
        )


def updateAddresses():
    client.ethernet_address = IPADDRESS.ipAddressGrabber("Ethernet")
    client.wifi_address = IPADDRESS.ipAddressGrabber("vEthernet (Custom)")
    client.hamachi_address = IPADDRESS.ipAddressGrabber("Hamachi")
    client.e4mc_address = MCLOG.parseLatestLogForE4MCAddress(settings.latest_log_path)


async def shutdown(forced_shutdown: bool):
    client.ethernet_address = ""
    client.wifi_address = ""
    client.hamachi_address = ""
    client.e4mc_address = ""

    await updateServerStatusEmbed(forced_shutdown=forced_shutdown)

    MSG.printWARNING(f"{client.user} is now shutting down")
    sys.exit(0)


client.run(settings.bot_token)  # MUST BE CALLED AFTER COMMAND DEFINITION
