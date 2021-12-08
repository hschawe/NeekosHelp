import discord
from discord.ext import commands
from NeekosHelp.helpers import checks


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.check_if_bot)
    async def myuserid(self, ctx):
        # get your discord user ID
        disc_userid = ctx.author.id
        mention = ctx.author.mention
        await ctx.channel.send(f"Your ID is {disc_userid}, {mention}!")

    @commands.command()
    @commands.check(checks.check_if_bot)
    @commands.check(checks.check_if_owner)
    async def updatemessage(self, ctx, *, msg):
        print("Changing status to", msg)
        activity = discord.Activity(name=msg, type=discord.ActivityType.listening)
        await self.bot.change_presence(activity=activity)


def setup(bot):
    bot.add_cog(Admin(bot))
