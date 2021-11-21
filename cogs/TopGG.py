import discord
import dbl
from discord.ext import commands
from NeekosHelp import keys
from NeekosHelp.helpers import checks


class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Set this to your DBL token
        self.token = keys.topgg_token
        # Autopost will post your guild count every 30 minutes
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        '''
        Uses dblpy's autopost feature to post guild count to top.gg every 30 minutes.
        '''
        print("Server count posted successfully")


def setup(bot):
    bot.add_cog(TopGG(bot))
