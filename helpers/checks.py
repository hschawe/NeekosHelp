from discord.ext import commands


def check_if_bot(ctx):
    if ctx.author.bot == True:
        print("command was used by a bot!")
        return False
    else:
        return True


def check_if_owner(ctx):
    """Check if command is used by the specified user ID"""
    if ctx.author.id == 169930632632336384 or ctx.author.id == 247205035983896576:
        return True
    else:
        return False
