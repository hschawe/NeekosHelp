import logging
import discord
from discord import app_commands
from discord.ext import commands
from helpers import checks


logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    """Class that holds all admin related commands"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="myuserid")
    @commands.is_owner()
    @commands.check(checks.check_if_bot)
    async def myuserid(self, interaction: discord.Interaction):
        """Command that returns discord user id"""
        disc_userid = interaction.user.id
        await interaction.response.send_message(f"Your ID is {disc_userid}!")

    @app_commands.command(name="updatemessage")
    @commands.is_owner()
    @commands.check(checks.check_if_bot)
    async def updatemessage(self, interaction: discord.Interaction, msg: str):
        """Command that updates bots status message"""
        logger.info(f"Changing the bot's status to {msg}")
        activity = discord.Activity(
            name=msg, type=discord.ActivityType.listening)
        await self.bot.change_presence(activity=activity)

    @app_commands.command(name="sync")
    @commands.is_owner()
    @commands.check(checks.check_if_bot)
    async def sync(self, interaction: discord.Interaction):
        """Command that syncs commands globally for slash command use"""
        logger.info("Syncing slash commands globally")
        await self.bot.tree.sync()
        embed = discord.Embed(
            description="Slash commands have been globally synchronized.",
            color=0x9C84EF,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="testsync")
    @commands.is_owner()
    @commands.check(checks.check_if_bot)
    async def testsync(self, interaction: discord.Interaction):
        """Command that syncs commands only to one guild for testing slash commands"""
        logger.info("Syncing slash commands to test discord")
        this_guild_id = interaction.guild.id
        test_guild = discord.Object(id=this_guild_id)

        self.bot.tree.copy_global_to(guild=test_guild)
        cmds = await self.bot.tree.sync(guild=test_guild)
        cmds_strs = str([cmd.name for cmd in cmds])

        embed = discord.Embed(
            description=f"Slash commands have been synchronized to the test discord (guild ID = {this_guild_id}).\n Synced: {cmds_strs}",
            color=0x9C84EF,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Discordpy cog setup function"""
    await bot.add_cog(Admin(bot))
