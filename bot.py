import discord
from discord.ext import commands
import keys

headers = keys.headers                  # Header for a Riot API request.
discord_bot_key = keys.discord_bot_key  # Discord bot key

# Run the Discord bot and add cogs
client = commands.Bot(command_prefix = '//', help_command = None)
client.load_extension("cogs.Basic")
client.load_extension("cogs.Admin")
if hasattr(keys, "topgg_token"):
    client.load_extension("cogs.TopGG")
client.load_extension("cogs.TFT")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # Set the Bot's status message (Listening to //help)
    activity = discord.Activity(name='//help', type=discord.ActivityType.listening)
    await client.change_presence(activity=activity)


client.run(discord_bot_key)