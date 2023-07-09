import logging
import discord
from discord.ext import commands
from helpers import checks


logger = logging.getLogger(__name__)


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
        await ctx.reply(f"Your ID is {disc_userid}, {mention}!")

    @commands.command()
    @commands.check(checks.check_if_bot)
    @commands.check(checks.check_if_owner)
    async def updatemessage(self, ctx, *, msg):
        """Command that updates bots status message"""
        logger.info(f"Changing the bot's status to {msg}")
        activity = discord.Activity(
            name=msg, type=discord.ActivityType.listening)
        await self.bot.change_presence(activity=activity)

    @commands.command()
    @commands.check(checks.check_if_bot)
    @commands.check(checks.check_if_owner)
    async def sync(self, ctx):
        """Command that syncs commands globally for slash command use"""
        logger.info("Syncing slash commands globally")
        await ctx.bot.tree.sync()
        embed = discord.Embed(
            description="Slash commands have been globally synchronized.",
            color=0x9C84EF,
        )
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.check(checks.check_if_bot)
    @commands.check(checks.check_if_owner)
    async def testsync(self, ctx):
        """Command that syncs commands only to one guild for testing slash commands"""
        logger.info("Syncing slash commands to test discord")
        this_guild_id = ctx.guild.id
        test_guild = discord.Object(id=this_guild_id)

        self.bot.tree.copy_global_to(guild=test_guild)
        cmds = await ctx.bot.tree.sync(guild=test_guild)
        cmds_strs = str([cmd.name for cmd in cmds])

        embed = discord.Embed(
            description=f"Slash commands have been synchronized to the test discord (guild ID = {this_guild_id}).\n Synced: {cmds_strs}",
            color=0x9C84EF,
        )
        await ctx.reply(embed=embed)



async def setup(bot):
    """Discordpy cog setup function"""
    await bot.add_cog(Admin(bot))
