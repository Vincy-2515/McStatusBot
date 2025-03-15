from datetime import datetime
import pyperclip
import sys
import discord
from discord.ext import commands
from discord.ext import tasks
import GetSettings
import resources.LatestLogParser as MCLOG
import resources.IpAddressGrabber as IP
import resources.ConsoleMessagesHandling as MSG

try:
    settings = GetSettings.Settings()
except Exception as e:
    MSG.printERROR(f"failed the collection of the settings from the file: {e}")

DATETIME_FORMAT = "%H:%M:%S %d.%m.%Y "
GUILD_ID = discord.Object(id=settings.id_server)


class Client(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.startup_time: str = ""
        self.after_online: bool = False

        self.player_count: int = 0
        self.server_status: str = ""
        self.previous_player_count: int = 0
        self.previous_server_status: str = ""

        self.ethernet_address: str = None
        self.hamachi_address: str = None
        self.e4mc_address: str = None

    async def on_ready(self):
        MSG.printINFO(f"logged in as {client.user} (ID: {client.user.id})")
        MSG.printWARNING("press [CTRL]+[C] to stop the bot, enjoy :)")

        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            MSG.printINFO(f"synchronized {len(synced)} command(s)")
        except Exception as e:
            MSG.printERROR(f"commands synchronization error: {e}")

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=GUILD_ID)
        self.updateServerStatus.start()

    @tasks.loop(seconds=settings.serverStatus_update_delay)
    async def updateServerStatus(self):
        self.server_status = MCLOG.parseLatestLogForServerStatus(settings.path_latest_log)
        self.player_count = MCLOG.parseLatestLogForPlayerCount(settings.path_latest_log)

        if self.server_status == "🟢 Online" and self.after_online == False:
            now = datetime.now()
            self.startup_time = now.strftime(DATETIME_FORMAT)
            self.after_online = True

            self.ethernet_address = IP.ipAddressGrabber("Ethernet")
            self.hamachi_address = IP.ipAddressGrabber("Hamachi")
            self.e4mc_address = MCLOG.parseLatestLogForE4MCAddress(settings.path_latest_log)

            await updateServerStatusEmbed()

            self.previous_player_count = self.player_count
            self.previous_server_status = self.server_status

        elif self.server_status == "🔴 Offline" and self.after_online == True:
            self.ethernet_address: str = None
            self.hamachi_address: str = None
            self.e4mc_address: str = None

            await updateServerStatusEmbed()

            MSG.printWARNING(f"The sever is offline, {client.user} is now shutting down")
            sys.exit(0)

        elif (self.previous_player_count != self.player_count) or (self.previous_server_status != self.server_status):
            await updateServerStatusEmbed()

            self.previous_player_count = self.player_count
            self.previous_server_status = self.server_status

        else:
            MSG.printINFO('"server_status" and "player_count" have not changed, skipping "updateServerStatusEmbed"')

    @updateServerStatus.before_loop
    async def beforeUpdateServerStatus(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="/", intents=intents)


### commands ##############################################################################


@client.tree.command(
    name="sendstatus", description="Invia un embed contenente lo stato del server e gli indirizzi per la connessione ad esso"
)
async def sendstatus(interaction: discord.Interaction):
    if await handleCommandInvocation(interaction=interaction, command_name="sendstatus", admin_only_command=True) == False:
        return

    await interaction.response.defer(thinking=True)

    server_status: str = MCLOG.parseLatestLogForServerStatus(settings.path_latest_log)
    player_count: int = MCLOG.parseLatestLogForPlayerCount(settings.path_latest_log)
    image, server_status_embed = getServerStatusEmbed(server_status, player_count)
    previous_message: discord.Message = await getMessage(settings.id_channel, settings.id_message_serverStatus)

    try:
        await previous_message.edit()
        await interaction.followup.send("Ho modificato il messaggio già esistente")
    except Exception as e:
        MSG.printWARNING(f"couldn't edit the server stauts message, sending a new message. Error: {e}")
        await interaction.followup.send(file=image, embed=server_status_embed)
        settings.updateSettings()


@client.tree.command(name="reloaddata", description="Ricarica tutti i dati che il bot raccoglie da vari files")
async def reloaddata(interaction: discord.Interaction):
    if await handleCommandInvocation(interaction=interaction, command_name="reloaddata", admin_only_command=True) == False:
        return

    await interaction.response.defer(thinking=True)

    try:
        settings.updateSettings()

        client.ethernet_address = IP.ipAddressGrabber("Ethernet")
        client.hamachi_address = IP.ipAddressGrabber("Hamachi")
        client.e4mc_address = MCLOG.parseLatestLogForE4MCAddress(settings.path_latest_log)

        client.server_status = MCLOG.parseLatestLogForServerStatus(settings.path_latest_log)
        client.player_count = MCLOG.parseLatestLogForPlayerCount(settings.path_latest_log)

        await updateServerStatusEmbed()

        MSG.printINFO("All data and settings are reloaded")
        await interaction.followup.send("Dati e impostazioni ricaricati")
    except Exception as e:
        MSG.printERROR(f"Reloading failed: {e}")
        await interaction.followup.send("Errore nel ricaricamento, controlla la console per ulteriori informazioni")


### other functions #######################################################################


async def updateServerStatusEmbed():
    try:
        previous_message: discord.Message = await getMessage(settings.id_channel, settings.id_message_serverStatus)
        image, server_status_embed = getServerStatusEmbed(client.server_status, client.player_count)

        await previous_message.edit(attachments=[image], embed=server_status_embed)
        MSG.printINFO(f'"server_status_embed" updated, server {client.server_status} with {client.player_count} players')
    except Exception as e:
        MSG.printERROR(f'failed "server_status_embed" update: {e}')


async def getMessage(id_channel: int, id_message: int) -> discord.Message:
    channel = client.get_channel(id_channel)

    try:
        if channel is not None:
            try:
                return await channel.fetch_message(id_message)
            except Exception as e:
                MSG.printERROR(f"Unable to fetch the message: {e}")
    except Exception as e:
        MSG.printERROR(f'Error with "id_channel": {e}')
        return None

    return None


def getServerStatusEmbed(server_status: str, player_count: int) -> discord.File | discord.Embed:
    splitted_path = settings.path_embed_image.split("/")
    imagename = splitted_path[len(splitted_path) - 1]
    image = discord.File(settings.path_embed_image, filename=imagename)

    server_status_embed = discord.Embed(title="parrot-trapping-wasabi", colour=discord.Color.green())

    # stato del server
    server_status_embed.add_field(name="Server Status:", value=server_status)
    if server_status == "🔴 Offline":
        server_status_embed.add_field(name="Players online:", value=f"0/{settings.max_players}")
    else:
        server_status_embed.add_field(name="Players online:", value=f"{player_count}/{settings.max_players}")

    server_status_embed.add_field(name="", value="")

    # indirizzi
    if client.ethernet_address != None or client.e4mc_address != None or client.hamachi_address != None:
        server_status_embed.add_field(name="Indirizzi per la connessione:", value="", inline=False)
    if client.ethernet_address != None:
        server_status_embed.add_field(
            name="",
            value=f"*Indirizzo locale:*||```{client.ethernet_address}```||",
            inline=False,
        )
    if client.e4mc_address != None:
        server_status_embed.add_field(
            name="",
            value=f"*Indirizzo e4mc:*||```{client.e4mc_address}```||",
            inline=False,
        )
    if client.hamachi_address != None:
        server_status_embed.add_field(
            name="",
            value=f"*Indirizzo Hamachi:*||```{client.hamachi_address}```||",
            inline=False,
        )

    server_status_embed.set_image(url=f"attachment://{imagename}")
    server_status_embed.set_footer(text=f"ultimo avvio: {client.startup_time}")

    return [image, server_status_embed]


async def handleCommandInvocation(interaction: discord.Interaction, command_name: str, admin_only_command: bool) -> bool:
    MSG.printINFO(f'"/{command_name}" invoked by {interaction.user}')

    if (str(interaction.user) not in settings.server_admins) and (admin_only_command == True):
        await interaction.response.send_message("Non puoi eseguire questo comando")
        return False
    return True


client.run(settings.bot_token)
