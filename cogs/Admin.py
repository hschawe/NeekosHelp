import discord
from discord.ext import commands
from helpers import checks


class Admin(commands.Cog):
    """Class that holds all admin related commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.check(checks.check_if_bot)
    async def myuserid(self, ctx):
        """Command that returns discord user id"""
        # get your discord user ID
        disc_userid = ctx.author.id
        mention = ctx.author.mention
        await ctx.channel.send(f"Your ID is {disc_userid}, {mention}!")

    @commands.hybrid_command()
    @commands.check(checks.check_if_bot)
    @commands.check(checks.check_if_owner)
    async def updatemessage(self, ctx, *, msg):
        """Command that updates bots status message"""
        print("Changing status to", msg)
        activity = discord.Activity(
            name=msg, type=discord.ActivityType.listening)
        await self.bot.change_presence(activity=activity)

    @commands.hybrid_command()
    @commands.check(checks.check_if_bot)
    @commands.check(checks.check_if_owner)
    async def sync(self, ctx):
        """Command that syncs commands globally for slash command use"""
        print("Syncing slash commands globally")
        await ctx.bot.tree.sync()
        embed = discord.Embed(
            description="Slash commands have been globally synchronized.",
            color=0x9C84EF,
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.check(checks.check_if_bot)
    @commands.check(checks.check_if_owner)
    async def testsync(self, ctx):
        """Command that syncs commands only to Neeko's Help discord for slash command use"""
        print("Syncing slash commands to test discord")
        test_guild = discord.Object(id=703660440374476811)
        ctx.bot.tree.clear_commands(guild=test_guild)
        await ctx.bot.tree.sync(guild=test_guild)

        cmds = await ctx.bot.tree.fetch_commands()
        cmds_strs = str([cmd.name for cmd in cmds])
        print(cmds_strs)

        embed = discord.Embed(
            description=f"Slash commands have been synchronized to the test discord (guild ID = 703660440374476811).\n Synced: {cmds_strs}",
            color=0x9C84EF,
        )
        await ctx.send(embed=embed)



async def setup(bot):
    """Discordpy cog setup function"""
    await bot.add_cog(Admin(bot))
