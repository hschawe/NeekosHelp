import logging
import discord
from discord.ext import commands
import keys
from helpers import helpers


logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s : %(asctime)s : %(message)s")
logger = logging.getLogger(__name__)

headers = keys.headers                  # Header for a Riot API request.
discord_bot_key = keys.discord_bot_key  # Discord bot key
environment = keys.environment
owner_id = keys.owner_id
test_guild_id = keys.guild_id
intents = discord.Intents.default()

# Run the Discord bot and add cogs
bot = commands.Bot(command_prefix='//', intents=intents, owner_id=169930632632336384)

@bot.event
async def on_ready():
    """Runs when bot is loaded."""
    logger.info(f"We have logged in as {bot.user}")

    logger.info("Mounting cogs...")
    await bot.load_extension("cogs.Basic")
    await bot.load_extension("cogs.Admin")
    await bot.load_extension("cogs.TFT")
    if environment == "prod":
        # TODO: Setup automatic posting server count to top.gg
        # await bot.load_extension("cogs.TopGG")
        pass
    logger.info("Done mounting cogs.")

    logger.info("Syncing slash commands to test discord...")
    await helpers.sync_to_guild(bot, test_guild_id)

    # Set the Bot's status message (Listening to //help)
    activity = discord.Activity(
        name='//helpmeneeko', type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity)

bot.run(discord_bot_key)
