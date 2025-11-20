import sys, time, discord, logging, datetime
from typing import Optional
import lib.bot.bot as BOT
import lib.globals as GLOBALS
import lib.utils.LatestLogParser as MCLOG
import lib.utils.IpAddressGrabber as IPADDRESS


logger = logging.getLogger(__name__)

## messages managing ##################################################################################################


async def editChoosenPreviousMessage(forced_shutdown: bool = False) -> bool:
    try:
        image, server_status_embed = getServerStatusEmbed()
    except Exception as e:
        raise Exception(f"An error occurred during the creation of the embed: {e}")

    try:
        previous_message = await getMessageObject(GLOBALS.settings.channel_id, GLOBALS.settings.message_id)
    except Exception as e:
        raise Exception(f"An error occurred while obtaining the message to edit: {e}")

    if isinstance(previous_message, discord.Message):

        updateServerStatusEmbed_start_time = time.perf_counter()

        logger.info("Editing previous message")
        await previous_message.edit(embed=server_status_embed, attachments=[image])

        updateServerStatusEmbed_finish_time = time.perf_counter()
        logger.info(
            f'It took {(updateServerStatusEmbed_finish_time - updateServerStatusEmbed_start_time):.2f} seconds to update "server_status_embed"'
        )
        return True

    image.close()
    raise Exception("This message is not a message")


async def sendNewMessageToChoosenChannel() -> bool:
    image, server_status_embed = getServerStatusEmbed()
    channel = BOT.client.get_channel(GLOBALS.settings.channel_id)

    if isinstance(channel, discord.TextChannel):
        updateServerStatusEmbed_start_time = time.perf_counter()

        await channel.send(file=image, embed=server_status_embed)

        updateServerStatusEmbed_finish_time = time.perf_counter()
        logger.info(
            f'It took {(updateServerStatusEmbed_finish_time - updateServerStatusEmbed_start_time):.2f} seconds to send "server_status_embed"'
        )
        image.close()
        return True

    image.close()
    raise Exception("This channel is not a channel")


async def getMessageObject(channel_id: int, message_id: int) -> Optional[discord.Message]:
    channel = BOT.client.get_channel(channel_id)

    if not isinstance(channel, discord.TextChannel):
        logger.error(f"The channel {channel_id} is not a TextChannel")
        return

    try:
        try:
            return await channel.fetch_message(message_id)
        except Exception as e:
            logger.error(f"Unable to fetch the message: {e}")
    except Exception as e:
        logger.error(f'Error with "id_channel": {e}')
        return None

    return None


## embed managing #####################################################################################################


async def updateServerStatusEmbed(forced_shutdown: bool = False):
    logger.info('Updating "server_status_embed"...')

    try:
        await editChoosenPreviousMessage(forced_shutdown)
    except Exception as e:
        logger.error(f"Couldn't edit the message: {e}")

    try:
        await sendNewMessageToChoosenChannel()
    except Exception as e:
        logger.error(f"Couldn't send the message: {e}")

    logger.info(f'server_status: "{BOT.client.server_status}", player_count: {BOT.client.player_count}')


def getServerStatusEmbed(forced_shutdown: bool = False) -> tuple[discord.File, discord.Embed]:
    splitted_path = GLOBALS.settings.embed_image_path.split("/")
    imagename = splitted_path[len(splitted_path) - 1]
    image = discord.File(GLOBALS.settings.embed_image_path, filename=imagename)

    server_status_embed = discord.Embed(title=GLOBALS.settings.server_name, colour=discord.Color.dark_gray())

    if BOT.client.server_status == MCLOG.STRING_SERVER_STATUS_OFFLINE:
        server_status_embed = discord.Embed(title=GLOBALS.settings.server_name, colour=discord.Color.red())

    elif BOT.client.server_status == MCLOG.STRING_SERVER_STATUS_ONLINE:
        server_status_embed = discord.Embed(
            title=GLOBALS.settings.server_name, colour=discord.Color.green(), timestamp=BOT.client.startup_time
        )

    elif BOT.client.server_status == MCLOG.STRING_SERVER_STATUS_STARTING:
        server_status_embed = discord.Embed(title=GLOBALS.settings.server_name, colour=discord.Color.yellow())

    addServerStatusFields(server_status_embed)
    if GLOBALS.settings.is_add_addresses_fields_enabled:
        addAddressesFields(server_status_embed)

    if forced_shutdown:
        server_status_embed.add_field(
            name="", value=":warning: Lo stato del server potrebbe non essere aggiornato", inline=False
        )

    server_status_embed.set_image(url=f"attachment://{imagename}")

    return image, server_status_embed


def addServerStatusFields(server_status_embed: discord.Embed):
    server_status_embed.add_field(name="Server Status:", value=BOT.client.server_status)
    if BOT.client.server_status == MCLOG.STRING_SERVER_STATUS_OFFLINE:
        server_status_embed.add_field(
            name="Players online:", value=f"<:steve:1382831305221472468> 0/{GLOBALS.settings.max_players}"
        )
    else:
        server_status_embed.add_field(
            name="Players online:",
            value=f"<:steve:1382831305221472468> {BOT.client.player_count}/{GLOBALS.settings.max_players}",
        )


def addAddressesFields(server_status_embed: discord.Embed):
    if len(BOT.client.ip_addresses) != 0 or BOT.client.e4mc_address != "":
        server_status_embed.add_field(name="Indirizzi per la connessione:", value="", inline=False)

    if len(BOT.client.ip_addresses) != 0:
        for i in range(len(BOT.client.ip_addresses)):
            if BOT.client.ip_addresses[i] != "":
                server_status_embed.add_field(
                    name="",
                    value=f"* __{GLOBALS.settings.network_cards[i]}:__||```{BOT.client.ip_addresses[i]}:{GLOBALS.settings.server_port}```||",
                    inline=False,
                )

    if BOT.client.e4mc_address != "":
        server_status_embed.add_field(name="", value=f"* __Indirizzo e4mc:__||```{BOT.client.e4mc_address}```||", inline=False)


## command helpers ####################################################################################################


async def handleCommandInvocation(interaction: discord.Interaction, command_name: str, admin_only_command: bool) -> bool:
    logger.info(f'"/{command_name}" invoked by {interaction.user}')

    if (str(interaction.user) not in GLOBALS.settings.bot_admins) and (admin_only_command == True):
        await interaction.response.send_message("Non puoi eseguire questo comando")
        logger.warning(f'{interaction.user} cannot run the command "/{command_name}"')
        return False
    return True


## other helpers ######################################################################################################


async def handleServerStatusChange():
    if BOT.client.server_status == MCLOG.STRING_SERVER_STATUS_ONLINE and BOT.client.after_online == False:
        logger.info("The server is online")

        if GLOBALS.settings.is_add_addresses_fields_enabled:
            updateAddresses()

        BOT.client.startup_time = datetime.datetime.now()
        BOT.client.after_online = True

    elif BOT.client.server_status == MCLOG.STRING_SERVER_STATUS_STARTING:
        logger.info("The server is starting")

    elif BOT.client.server_status == MCLOG.STRING_SERVER_STATUS_OFFLINE and BOT.client.after_online == True:
        logger.info("The server is offline, starting shutdown procedure...")
        await shutdown(forced_shutdown=False)


def updateAddresses():
    if not GLOBALS.settings.is_add_addresses_fields_enabled:
        logger.info("'is_add_addresses_fields_enabled' is disabled, skipping address update")
        return

    for i in range(len(GLOBALS.settings.network_cards)):
        BOT.client.ip_addresses.append(IPADDRESS.ipAddressGrabber(GLOBALS.settings.network_cards[i]))

    if GLOBALS.settings.is_show_e4mc_address_enabled:
        BOT.client.e4mc_address = MCLOG.parseLatestLogForE4MCAddress(GLOBALS.settings.latest_log_path)


def updatePreviousValues():
    BOT.client.previous_player_count = BOT.client.player_count
    BOT.client.previous_server_status = BOT.client.server_status
    BOT.client.cycles_count = 0


async def shutdown(forced_shutdown: bool):
    BOT.client.ip_addresses = []
    BOT.client.e4mc_address = ""

    await updateServerStatusEmbed(forced_shutdown=forced_shutdown)

    logger.warning(f"{BOT.client.user} is now shutting down")
    sys.exit(0)
