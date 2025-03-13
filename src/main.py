from datetime import datetime
import sys
import discord
from discord.ext import commands
from discord.ext import tasks
import GetValues
import resources.LatestLogParser as MCLOG
import resources.IpAddressGrabber as IP
import resources.ConsoleMessagesHandling as MSG

try:
    settings = GetValues.Settings()
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

    async def on_ready(self):
        MSG.printINFO(f"logged in as {client.user} (ID: {client.user.id})")
        MSG.printWARNING("press [CTRL]+[C] to stop the bot, enjoy :)")

        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            MSG.printINFO(f"syncronized {len(synced)} command(s)")
        except Exception as e:
            MSG.printERROR(f"commands syncronization error: {e}")

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=GUILD_ID)
        self.updateServerStatus.start()
        self.updateServerStatusEmbed.start()

    @tasks.loop(seconds=settings.update_delay_serverStatus)
    async def updateServerStatus(self):
        self.server_status = MCLOG.parseLatestLogForServerStatus(settings.path_latest_log)
        self.player_count = MCLOG.parseLatestLogForPlayerCount(settings.path_latest_log)
        
        if self.server_status == "🟢 Online" and self.after_online == False:
            now = datetime.now()
            self.startup_time = now.strftime(DATETIME_FORMAT)
            self.after_online = True

            try:
                previous_message = await getMessage(settings.id_channel, settings.id_message_addresses)
                addresses_embed = getAddressesEmbed()
                await previous_message.edit(embed=addresses_embed)
            except Exception as e:
                MSG.printERROR(f"could not update the addresses message: {e}")

        elif self.server_status == "🔴 Offline" and self.after_online == True:
            try:
                previous_message: discord.Message = await getMessage(settings.id_channel, settings.id_message_serverStatus)
                image, server_status_embed = getServerStatusEmbed(self.server_status, self.player_count)
                await previous_message.edit(attachments=[image], embed=server_status_embed)
                MSG.printINFO(f'"server_status_embed" updated, server {self.server_status} with {self.player_count} players')
            except Exception as e:
                MSG.printERROR(f'failed "server_status_embed" update: {e}')

            MSG.printWARNING(f"The sever is offline, {client.user} is now shutting down")
            sys.exit(0)

    @tasks.loop(seconds=settings.update_delay_serverStatusEmbed)
    async def updateServerStatusEmbed(self):
        if (self.previous_player_count != self.player_count) or (self.previous_server_status != self.server_status):
            try:
                previous_message: discord.Message = await getMessage(settings.id_channel, settings.id_message_serverStatus)
                image, server_status_embed = getServerStatusEmbed(self.server_status, self.player_count)
                await previous_message.edit(attachments=[image], embed=server_status_embed)
                MSG.printINFO(f'"server_status_embed" updated, server {self.server_status} with {self.player_count} players')
            except Exception as e:
                MSG.printERROR(f'failed "server_status_embed" update: {e}')
                
            self.previous_player_count = self.player_count
            self.previous_server_status = self.server_status
        else:
            MSG.printINFO('"server_status" and "player_count" have not changed, skipping "updateServerStatusEmbed"')


    @updateServerStatus.before_loop
    async def beforeUpdateServerStatus(self):
        await self.wait_until_ready()

    @updateServerStatusEmbed.before_loop
    async def beforeUpdateServerStatusEmbed(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="/", intents=intents)


### commands ##############################################################################


@client.tree.command(name="sendaddresses", description="Invia gli indirizzi per il colegamento al server")
async def sendaddresses(interaction: discord.Interaction):
    MSG.printINFO(f'"/sendaddresses" invoked by {interaction.user}')
    await interaction.response.defer()
    previous_message: discord.Message = await getMessage(settings.id_channel, settings.id_message_addresses)
    addresses_embed: discord.Embed = getAddressesEmbed()

    try:
        await previous_message.edit(embed=addresses_embed)
        await interaction.followup.send("Ho modificato il messaggio già esistente")
    except Exception as e:
        MSG.printWARNING(f"couldn't edit the addresses message, sending a new message. Error: {e}")
        await interaction.followup.send(embed=addresses_embed)
        settings.updateSettings()
        


@client.tree.command(name="sendstatus", description="Invia lo stato del server")
async def sendstatus(interaction: discord.Interaction):
    MSG.printINFO(f'"/sendstatus" invoked by {interaction.user}')
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
        


### other functions #######################################################################


def getAddressesEmbed() -> discord.Embed:
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)

    addresses_embed = discord.Embed(
        title="parrot-trapping-wasabi",
        description="Indirizzi per la connessione al server",
        colour=discord.Color.green(),
    )
    addresses_embed.add_field(
        name="Indirizzo locale:",
        value=f'||{IP.ipAddressGrabber("Ethernet")}||',
        inline=False,
    )
    addresses_embed.add_field(
        name="Indirizzo Hamachi:",
        value=f'||{IP.ipAddressGrabber("Hamachi")}||',
        inline=False,
    )
    addresses_embed.add_field(
        name="Indirizzo e4mc:",
        value=f"||{MCLOG.parseLatestLogE4MCAddress(settings.path_latest_log)}||",
        inline=False,
    )
    addresses_embed.set_footer(text=f"ultimo aggiornamento: {current_time}")

    return addresses_embed


def getServerStatusEmbed(server_status: str, player_count: int) -> discord.File | discord.Embed:
    splitted_path = settings.path_embed_image.split("/")
    imagename = splitted_path[len(splitted_path) - 1]
    image = discord.File(settings.path_embed_image, filename=imagename)

    server_status_embed = discord.Embed(title="parrot-trapping-wasabi", colour=discord.Color.green())
    server_status_embed.add_field(name="Server Status:", value=server_status)
    if server_status == "🔴 Offline":
        server_status_embed.add_field(name="Players online:", value=f"0/{settings.max_players}")
    else:
        server_status_embed.add_field(name="Players online:", value=f"{player_count}/{settings.max_players}")
    server_status_embed.set_image(url=f"attachment://{imagename}")
    server_status_embed.set_footer(text=f"ultimo avvio: {client.startup_time}")

    return [image, server_status_embed]


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


client.run(settings.bot_token)
