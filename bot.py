import discord
from discord.ext import commands
import keys

headers = keys.headers                  # Header for a Riot API request.
discord_bot_key = keys.discord_bot_key  # Discord bot key
environment = keys.environment
intents = discord.Intents.default()
intents.message_content = True

# Run the Discord bot and add cogs
bot = commands.Bot(command_prefix='//', intents=intents)


@bot.event
async def on_ready():
    """Runs when bot is loaded."""
    await bot.load_extension("cogs.Basic")
    await bot.load_extension("cogs.Admin")
    await bot.load_extension("cogs.TFT")
    if environment == "prod":
        await bot.load_extension("cogs.TopGG")
    print(f"We have logged in as {bot.user}")
    # Set the Bot's status message (Listening to //help)
    activity = discord.Activity(
        name='//helpmeneeko', type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity)

bot.run(discord_bot_key)
