import discord
from discord.ext import commands
from discord import app_commands
from helpers import checks


class Basic(commands.Cog):
    """Class for basic bot commands"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping")
    @commands.check(checks.check_if_bot)
    async def ping(self, interaction: discord.Interaction):
        """Command that returns pong!"""
        await interaction.response.send_message('pong!')

    @app_commands.command(name="help")
    @commands.check(checks.check_if_bot)
    async def help(self, interaction: discord.Interaction):
        """Command that returns help message."""
        msg = "\n**/recentmatch** *[region] [summoner]* - gives the most recent TFT match for the specified summoner\n\
    **/matchhistory** *[region] [summoner]* - gives a list of TFT matches for the specified summoner. Add a reaction to view detailed match info!\n\
    **/tftrank** *[region] [summoner]* - gives the summoner's tft rank\n\
    **/table** *[table type]* - gives the requested loot table\n\
    **/piltoverstacks** *[stacks]* - gives the piltover cashout table at that number of stacks\n\
    **/regions** - gives a list of region codes (used in other commands)\n\
    **/ping** - returns pong!\n"

        support_server = "Join the support server to request new commands or report bugs: **https://discord.gg/n7Dtk43GpU**"

        privacy_policy = "https://neekos.help/privacy"

        embed_msg = discord.Embed(
            colour=discord.Colour.green()
        )
        embed_msg.add_field(name="Command List", value=msg, inline=False)
        embed_msg.add_field(name="View our Privacy Policy at",
                            value=privacy_policy, inline=False)
        embed_msg.add_field(name="Need more help?",
                            value=support_server, inline=False)

        await interaction.response.send_message(embed=embed_msg)


async def setup(bot):
    """Discordpy cog setup function"""
    await bot.add_cog(Basic(bot))
