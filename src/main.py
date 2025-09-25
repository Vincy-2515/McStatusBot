import time
import datetime
import sys
import discord
from discord.ext import commands
from discord.ext import tasks
import GetSettings
import resources.LatestLogParser as MCLOG
import resources.ConsoleMessagesHandling as MSG

try:
    settings = GetSettings.Settings()
except Exception as e:
    MSG.printERROR(f"failed the collection of the settings from the file: {e}")

GUILD_ID = discord.Object(id=settings.id_server)

class Client(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.startup_time: datetime.datetime = None
        self.after_online: bool = False

        self.player_count: int = 0
        self.server_status: str = ""
        self.previous_player_count: int = 0
        self.previous_server_status: str = ""
        self.cycles_count = 0

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

        if (self.previous_player_count != self.player_count) or (self.previous_server_status != self.server_status):
            MSG.printINFO(f'Values have changed after {self.cycles_count} cycles (or {self.cycles_count * settings.serverStatus_update_delay} seconds)')

            if self.server_status == MCLOG.STRING_SERVER_STATUS_ONLINE and self.after_online == False:
                MSG.printINFO("The server is online")

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

    image, server_status_embed = getServerStatusEmbed()
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

        client.server_status = MCLOG.parseLatestLogForServerStatus(settings.path_latest_log)
        client.player_count = MCLOG.parseLatestLogForPlayerCount(settings.path_latest_log)

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

async def updateServerStatusEmbed(forced_shutdown: bool = None):
    MSG.printINFO('Updating "server_status_embed"...')
    updateServerStatusEmbed_start_time = time.perf_counter()

    try:
        previous_message: discord.Message = await getMessage(settings.id_channel, settings.id_message_serverStatus)
        image, server_status_embed = getServerStatusEmbed(forced_shutdown=forced_shutdown)

        await previous_message.edit(
            attachments=[image], embed=server_status_embed
        )  ################################### TROPPO CONSUMO DI TEMPO
    except Exception as e:
        settings.updateSettings()
        MSG.printERROR(f'failed "server_status_embed" update: {e}')
        MSG.printINFO("sending a new message")
        channel: discord.TextChannel = client.get_channel(settings.id_channel)
        await channel.send(file=image, embed=server_status_embed)

    updateServerStatusEmbed_finish_time = time.perf_counter()
    MSG.printINFO(f'It took {(updateServerStatusEmbed_finish_time - updateServerStatusEmbed_start_time):.2f} seconds to update "server_status_embed"')
    MSG.printINFO(f'server_status: "{client.server_status}", player_count: {client.player_count}')

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

def getServerStatusEmbed(forced_shutdown: bool = None) -> discord.File | discord.Embed:
    splitted_path = settings.path_embed_image.split("/")
    imagename = splitted_path[len(splitted_path) - 1]
    image = discord.File(settings.path_embed_image, filename=imagename)

    if client.server_status == MCLOG.STRING_SERVER_STATUS_OFFLINE:
        server_status_embed = discord.Embed(title="Reworked", colour=discord.Color.red(), timestamp=client.startup_time)
    elif client.server_status == MCLOG.STRING_SERVER_STATUS_ONLINE:
        server_status_embed = discord.Embed(title="Reworked", colour=discord.Color.green(), timestamp=client.startup_time)
    elif client.server_status == MCLOG.STRING_SERVER_STATUS_STARTING:
        server_status_embed = discord.Embed(title="Reworked", colour=discord.Color.yellow(), timestamp=client.startup_time)

    # stato del server
    server_status_embed.add_field(name="Server Status:", value=client.server_status)
    if client.server_status == MCLOG.STRING_SERVER_STATUS_OFFLINE:
        server_status_embed.add_field(name="Players online:", value=f"<:steve:1382831305221472468> 0/{settings.max_players}")
    else:
        server_status_embed.add_field(
            name="Players online:", value=f"<:steve:1382831305221472468> {client.player_count}/{settings.max_players}"
        )

    if forced_shutdown:
        server_status_embed.add_field(
            name="", value="Attenzione! Lo stato del server potrebbe non essere aggiornato", inline=False
        )

    server_status_embed.set_image(url=f"attachment://{imagename}")

    return [image, server_status_embed]

async def handleCommandInvocation(interaction: discord.Interaction, command_name: str, admin_only_command: bool) -> bool:
    MSG.printINFO(f'"/{command_name}" invoked by {interaction.user}')

    if (str(interaction.user) not in settings.server_admins) and (admin_only_command == True):
        await interaction.response.send_message("Non puoi eseguire questo comando")
        return False
    return True

def updatePreviousValues():
    client.previous_player_count = client.player_count
    client.previous_server_status = client.server_status
    client.cycles_count = 0

async def shutdown(forced_shutdown: bool):
    await updateServerStatusEmbed(forced_shutdown=forced_shutdown)

    MSG.printWARNING(f"{client.user} is now shutting down")
    sys.exit(0)


client.run(settings.bot_token)
