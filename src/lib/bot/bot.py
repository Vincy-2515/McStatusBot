import discord, logging, datetime
from discord.ext import commands
from discord.ext import tasks
from typing import Any
import lib.globals as GLOBALS
import lib.bot.botHelperFunctions as HELPERS
import lib.utils.LatestLogParser as MCLOG


logger = logging.getLogger(__name__)


class Client(commands.Bot):
    def __init__(self, *args: tuple[Any], **kwargs: dict[str, Any]):
        super().__init__(*args, **kwargs)

        self.__guild: discord.Object

        self.startup_time: datetime.datetime
        self.after_online: bool = False

        self.player_count: int = 0
        self.server_status: str = ""
        self.previous_player_count: int = 0
        self.previous_server_status: str = ""
        self.cycles_count = 0

        self.ip_addresses: list[str] = []
        self.e4mc_address: str = ""

    async def setup_hook(self) -> None:
        self.__guild = discord.Object(id=GLOBALS.settings.server_id)
        self.tree.copy_global_to(guild=self.__guild)
        self.updateServerStatus.start()

    async def on_ready(self):
        if client.user is None:
            logger.error("The bot user is not initialized.")
            return

        logger.info(f"Logged in as {client.user} (ID: {client.user.id})")
        logger.info("The bot has successfully started, enjoy :)")

        try:
            synced = await self.tree.sync(guild=self.__guild)
            logger.info(f"Synchronized {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Commands synchronization error: {e}")

    @tasks.loop(seconds=GLOBALS.settings.server_status_update_delay)
    async def updateServerStatus(self):
        self.server_status = MCLOG.parseLatestLogForServerStatus(GLOBALS.settings.latest_log_path)
        self.player_count = MCLOG.parseLatestLogForPlayerCount(GLOBALS.settings.latest_log_path)

        if (self.previous_player_count != self.player_count) or (self.previous_server_status != self.server_status):
            logger.info(
                f"Values have changed after {self.cycles_count} cycles (or {self.cycles_count * GLOBALS.settings.server_status_update_delay} seconds)"
            )

            await HELPERS.handleServerStatusChange()

            await HELPERS.updateServerStatusEmbed()
            HELPERS.updatePreviousValues()

        else:
            self.cycles_count += 1

    @updateServerStatus.before_loop
    async def beforeUpdateServerStatus(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="/", intents=intents)  # type: ignore

## bot commands ################################################################################################################


@client.tree.command(
    name="sendstatus", description="Invia un embed contenente lo stato del server e gli indirizzi per la connessione ad esso"
)
async def sendstatus(interaction: discord.Interaction):
    if (
        await HELPERS.handleCommandInvocation(interaction=interaction, command_name="sendstatus", admin_only_command=True)
        == False
    ):
        return

    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        await HELPERS.editChoosenPreviousMessage()
        await interaction.followup.send("Ho modificato il messaggio già esistente")
        return
    except Exception as e:
        logger.error(f"Couldn't edit the message: {e}")

    try:
        await HELPERS.sendNewMessageToChoosenChannel()
        await interaction.followup.send("Ho inviato un nuovo messaggio, non ho potuto modificare quello esistente")
    except Exception as e:
        logger.error(f"Couldn't send the message: {e}")


@client.tree.command(name="reloaddata", description="Ricarica tutti i dati che il bot raccoglie da vari files")
async def reloaddata(interaction: discord.Interaction):
    if (
        await HELPERS.handleCommandInvocation(interaction=interaction, command_name="reloaddata", admin_only_command=True)
        == False
    ):
        return

    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        GLOBALS.settings.updateSettings(GLOBALS.config_toml_path)

        if GLOBALS.settings.is_add_addresses_fields_enabled:
            HELPERS.updateAddresses()

        client.server_status = MCLOG.parseLatestLogForServerStatus(GLOBALS.settings.latest_log_path)
        client.player_count = MCLOG.parseLatestLogForPlayerCount(GLOBALS.settings.latest_log_path)

        await HELPERS.updateServerStatusEmbed()

        logger.info("All data and GLOBALS.settings are reloaded")
        await interaction.followup.send("Dati e impostazioni ricaricati")
    except Exception as e:
        logger.error(f"Reloading failed: {e}")
        await interaction.followup.send("Errore nel ricaricamento, controlla la console per ulteriori informazioni")


@client.tree.command(name="shutdownbot", description="Manda il bot offline")
async def shutdownbot(interaction: discord.Interaction):
    if (
        await HELPERS.handleCommandInvocation(interaction=interaction, command_name="shutdownbot", admin_only_command=True)
        == False
    ):
        return

    await interaction.response.send_message("Sto per andare offline", ephemeral=True)
    await HELPERS.shutdown(forced_shutdown=True)


def run():
    client.run(GLOBALS.settings.bot_token, log_handler=None)  # MUST BE CALLED AFTER COMMAND DEFINITION
