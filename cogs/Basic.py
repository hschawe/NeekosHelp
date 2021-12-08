import discord
from discord.ext import commands
from helpers import checks


class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.check_if_bot)
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command()
    @commands.check(checks.check_if_bot)
    async def help(self, ctx):
        msg = "\n**//recentmatch** *[region] [summoner]* - gives the most recent TFT match for the specified summoner\n\
    **//matchhistory** *[region] [summoner]* - gives a list of TFT matches for the specified summoner. Add a reaction to view detailed match info!\n\
    **//tftrank** *[region] [summoner]* - gives the summoner's tft rank\n\
    **//regions** - gives a list of region codes (used in other commands)\n\
    **//ping** - returns pong!\n"

        support_server = "Join the support server to request new commands or report bugs: **https://discord.gg/ZC4m7ut**"

        embed_msg = discord.Embed(
            colour=discord.Colour.green()
        )
        embed_msg.add_field(name="Command List", value=msg, inline=False)
        embed_msg.add_field(name="Need more help?", value=support_server, inline=False)

        await(ctx.channel.send(embed=embed_msg))


def setup(bot):
    bot.add_cog(Basic(bot))
