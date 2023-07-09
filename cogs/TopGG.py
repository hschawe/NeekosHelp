import logging
import dbl
from discord.ext import commands
import keys


logger = logging.getLogger(__name__)


class TopGG(commands.Cog):
    """Class for TopGG bot commands"""

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
        logger.info("Server count posted successfully")


def setup(bot):
    """Discordpy setup function for cog."""
    bot.add_cog(TopGG(bot))
