from discord.ext import commands


def check_if_bot(ctx):
    if ctx.author.bot == True:
        print("command was used by a bot!")
        return False
    else:
        return True
