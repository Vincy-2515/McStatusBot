from datetime import datetime
import sys
import discord
from discord.ext import commands
from discord.ext import tasks
import GetValues
import src.LatestLogParser as MCLOG
import src.IpAddressGrabber as IP
import src.ConsoleMessagesHandling as MSG

try:
    settings = GetValues.Settings()
    settings.updateValues()
except Exception as e:
    MSG.printERROR(f"failed the collection of the settings from the file: {e}")

DATETIME_FORMAT = "%H:%M:%S %d.%m.%Y "
GUILD_ID = discord.Object(id=settings.server_id)

class Client(commands.Bot):    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player_count = 0
        self.server_status = ""
        self.after_online = False
        self.startup_time = ""

    async def on_ready(self):
        MSG.printINFO(f'logged in as {client.user} (ID: {client.user.id})')
        MSG.printWARNING("press [CTRL]+[C] to stop the bot, enjoy :)")

        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            MSG.printINFO(f'syncronized {len(synced)} command(s)')
        except Exception as e:
            MSG.printERROR(f'commands syncronization error: {e}')

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=GUILD_ID)        
        self.updateServerStatusEmbed.start()

    @tasks.loop(seconds=settings.updateServerStatusEmbed_task_delay)
    async def updateServerStatusEmbed(self):
        
        try:
            channel = self.get_channel(settings.channel_id)
            previous_message = await channel.fetch_message(settings.server_status_message_id)
            self.player_count = MCLOG.parseLatestLogForPlayerCount(settings.latest_log_path)
            self.server_status = MCLOG.parseLatestLogForServerStatus(settings.latest_log_path)
            server_status_embed = getServerStatusEmbed (self.server_status, self.player_count)
            await previous_message.edit(embed=server_status_embed)
            MSG.printINFO(f'"server_status_embed" updated, server {self.server_status} with {self.player_count} players')

        except Exception as e:
            MSG.printERROR(f'failed "server_status_embed" update: {e}')
            settings.updateValues()
            return
        
        if self.server_status == "🟢 Online" and self.after_online == False:
            now = datetime.now()
            self.startup_time = now.strftime(DATETIME_FORMAT)
            self.after_online = True

            previous_message = await getMessage(settings.channel_id, settings.addresses_message_id)
            addresses_embed = await getAddressesEmbed()

            if previous_message is not None:
                previous_message.edit(embed=addresses_embed)
        elif self.server_status == "🔴 Offline" and self.after_online == True:
            sys.exit(0)

    @updateServerStatusEmbed.before_loop
    async def beforeUpdateServerStatusEmbed(self):
        await self.wait_until_ready()

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="/", intents=intents)



### commands #########################################################################################################

@client.tree.command(name="sendaddresses", description="Invia gli indirizzi per il colegamento al server")
async def sendaddresses(interaction: discord.Interaction):
    MSG.printINFO(f'"/sendaddresses" invoked by {interaction.user}')
    await interaction.response.defer()
    previous_message = await getMessage(settings.channel_id, settings.addresses_message_id)
    addresses_embed = getAddressesEmbed()

    if previous_message is not None:
        previous_message.edit(embed=addresses_embed)
        await interaction.followup.send("Ho modificato il messaggio già esistente")
    else:
        MSG.printERROR(f"couldn't edit the addresses message, sending a new message")
        await interaction.followup.send(embed=addresses_embed)
        settings.updateValues()

@client.tree.command(name="sendstatus", description="Invia lo stato del server")
async def sendstatus(interaction: discord.Interaction):
    MSG.printINFO(f'"/sendstatus" invoked by {interaction.user}')
    await interaction.response.defer(thinking=True) 

    server_status = MCLOG.parseLatestLogForServerStatus(settings.latest_log_path)
    player_count = MCLOG.parseLatestLogForPlayerCount(settings.latest_log_path)

    server_status_embed = getServerStatusEmbed (server_status, player_count)

    await interaction.followup.send(embed=server_status_embed)



### other functions ##################################################################################################

def getAddressesEmbed () -> discord.Embed:
    now = datetime.now()
    current_time = now.strftime(DATETIME_FORMAT)

    addresses_embed = discord.Embed(title="parrot-trapping-wasabi",
                        description="Indirizzi per la connessione al server", 
                        colour=discord.Color.green())
    addresses_embed.add_field(name="Indirizzo locale:", value=f'||{IP.ipAddressGrabber("Ethernet")}||', inline=False)
    addresses_embed.add_field(name="Indirizzo Hamachi:", value=f'||{IP.ipAddressGrabber("Hamachi")}||', inline=False)
    addresses_embed.add_field(name="Indirizzo e4mc:", value=f'||{MCLOG.parseLatestLogE4MCAddress(settings.latest_log_path)}||', inline=False)
    addresses_embed.set_footer(text=f"ultimo aggiornamento: {current_time}")

    return addresses_embed

def getServerStatusEmbed (server_status: str, player_count: int) -> discord.Embed:
    server_status_embed = discord.Embed(title="parrot-trapping-wasabi",
                        colour=discord.Color.green())
    server_status_embed.add_field(name="Server Status:", value=server_status)
    if server_status == "🔴 Offline":
        server_status_embed.add_field(name="Players online:", value=f'0/{settings.max_players}')
    else:
        server_status_embed.add_field(name="Players online:", value=f'{player_count}/{settings.max_players}')
    server_status_embed.set_footer(text=f"ultimo avvio: {client.startup_time}")

    return server_status_embed

async def getMessage (channel_id:int, message_id:int):
    channel = client.get_channel(channel_id)

    try:
        if channel is not None:
            try:
                await channel.fetch_message(message_id)
            except Exception as e:
                MSG.printERROR(f"Unable to fetch the message: {e}")
    except discord.errors.NotFound:
        return None
    
    return None

client.run(settings.bot_token)
