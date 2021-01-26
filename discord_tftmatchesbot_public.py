#discord_tftmatchesbot_0.4.0.py
import os
import requests
import time
import json
import discord
from discord.ext import commands
import dbl

# Header for a Riot API request.
global headers
headers = {'HEADER_GOES_HERE'}


################################################################################
'''  Relevant information about the past and current TFT sets.
    (set 3 and onward.)

    Creates dictionaries to API-retrieved data to readable data (item names,
    synergy names, etc.).
'''

global queue_type_decoder
global item_decoder
global galaxy_decoder
global synergy_decoder
global name_decoder
global chosen_decoder
global region_decoder

# I made the set 3 decoders manually so I'm re-using them here instead of
# running create_decoders_from_file.py on the set 3 data
queue_type_decoder = {1090:"Normal",
                      1100:"Ranked",
                      1110:"TFT Tutorial"
                      }

item_decoder = {1:"B.F. Sword", 2:"Recurve Bow", 3:"Needlessly Large Rod", 4:"Tear of the Goddess",
                5:"Chain Vest", 6:"Negatron Cloak", 7:"Giant's Belt", 8:"Spatula",
                9:"Sparring Gloves", 11:"Deathblade", 12:"Giant Slayer", 13:"Hextech Gunblade",
                14:"Spear of Shojin", 15:"Guardian Angel", 16:"Bloodthirster", 17:"Zeke's Herald",
                18:"Blade of the Ruined King", 19:"Infinity Edge", 22:"Rapid Firecannon",
                23:"Guinsoo's Rageblade", 24:"Statikk Shiv", 25:"Titan's Resolve", 26:"Runaan's Hurricane",
                27:"Zz'Rot Portal", 28:"Infiltrator's Talons", 29:"Last Whisper", 33:"Rabadon's Deathcap",
                34:"Luden's Echo", 35:"Locket of the Iron Solari", 36:"Ionic Spark", 37:"Morellonomicon",
                38:"Battlecast Armor", 39:"Jeweled Gauntlet", 44:"Blue Buff",
                45:"Frozen Heart", 46:"Chalice of Power", 47:"Redemption", 48:"Star Guardian's Charm",
                49:"Hand of Justice", 55:"Bramble Vest", 56:"Sword Breaker", 57:"Red Buff",
                58:"Rebel Medal", 59:"Shroud of Stillness", 66:"Dragon's Claw", 67:"Zephyr",
                68:"Celestial Orb", 69:"Quicksilver", 77:"Warmog's Armor", 78:"Protector's Chestguard",
                79:"Trap Claw", 88:"Force of Nature", 89:"Dark Star's Heart", 99:"Thief's Gloves"
                }

galaxy_decoder = {"TFT3_GameVariation_None":"Normal Galaxy",
                  "TFT3_GameVariation_BigLittleLegends":"Medium Legends",
                  "TFT3_GameVariation_FourCostFirstCarousel":"Lilac Nebula",
                  "TFT3_GameVariation_FreeNeekos":"The Neekoverse",
                  "TFT3_GameVariation_FreeRerolls":"Trade Sector",
                  "TFT3_GameVariation_MidGameFoN":"Superdense Galaxy",
                  "TFT3_GameVariation_TwoStarCarousels":"Star Cluster",
                  "TFT3_GameVariation_Bonanza":"Treasure Trove",
                  "TFT3_GameVariation_LittlerLegends":"Little Little Legends",
                  "TFT3_GameVariation_StartingItems":"Galactic Armory",
                  "TFT3_GameVariation_SmallerBoards":"Dwarf Planet",
                  "TFT3_GameVariation_TwoItemMax":"Binary Star",
                  }

synergy_decoder = {'Astro 1': 'Astro',
                   'Battlecast 1': '2 Battlecast',
                   'Battlecast 2': '4 Battlecast',
                   'Battlecast 3': '6 Battlecast',
                   'Battlecast 4': '9 Battlecast',
                   'Set3_Blademaster 1': '3 Blademaster',
                   'Set3_Blademaster 2': '6 Blademaster',
                   'Set3_Blademaster 3': '9 Blademaster',
                   'Blaster 1': '2 Blaster',
                   'Blaster 2': '4 Blaster',
                   'Set3_Brawler 1': '2 Brawler',
                   'Set3_Brawler 2': '4 Brawler',
                   'Set3_Celestial 1': '2 Celestial',
                   'Set3_Celestial 2': '4 Celestial',
                   'Set3_Celestial 3': '6 Celestial',
                   'Chrono 1': '2 Chrono',
                   'Chrono 2': '4 Chrono',
                   'Chrono 3': '6 Chrono',
                   'Cybernetic 1': '3 Cybernetic',
                   'Cybernetic 2': '6 Cybernetic',
                   'DarkStar 1': '2 Dark Star',
                   'DarkStar 2': '4 Dark Star',
                   'DarkStar 3': '6 Dark Star',
                   'DarkStar 4': '8 Dark Star',
                   'Demolitionist 1': 'Demolitionist',
                   'Infiltrator 1': '2 Infiltrator',
                   'Infiltrator 2': '4 Infiltrator',
                   'Infiltrator 3': '6 Infiltrator',
                   'ManaReaver 1': 'Mana-Reaver',
                   'MechPilot 1': 'Mech-Pilot',
                   'Mercenary 1': 'Mercenary',
                   'Mercenary 2': 'Mercenary',
                   'Set3_Mystic 1': '2 Mystic',
                   'Set3_Mystic 2': '4 Mystic',
                   'Paragon 1': 'Paragon',
                   'Protector 1': '2 Protector',
                   'Protector 2': '4 Protector',
                   'Protector 3': '6 Protector',
                   'Rebel 1': '3 Rebel',
                   'Rebel 2': '6 Rebel',
                   'Rebel 3': '9 Rebel',
                   'Sniper 1': '2 Sniper',
                   'Sniper 2': '4 Sniper',
                   'Set3_Sorcerer 1': '3 Sorcerer',
                   'Set3_Sorcerer 2': '4 Sorcerer',
                   'Set3_Sorcerer 3': '6 Sorcerer',
                   'Set3_Sorcerer 4': '8 Sorcerer',
                   'SpacePirate 1': '2 Space Pirate',
                   'SpacePirate 2': '4 Space Pirate',
                   'StarGuardian 1': '3 Star Guardian',
                   'StarGuardian 2': '6 Star Guardian',
                   'Starship 1': 'Starship',
                   'Valkyrie 1': 'Valkyrie',
                   'Vanguard 1': '2 Vanguard',
                   'Vanguard 2': '4 Vanguard',
                   'Set3_Void 1': 'Void',
                   'Set4_Adept 1': '2 Adept',
                   'Set4_Adept 2': '3 Adept',
                   'Set4_Adept 3': '4 Adept',
                   'Set4_Assassin 1': '2 Assassin',
                   'Set4_Assassin 2': '4 Assassin',
                   'Set4_Assassin 3': '6 Assassin',
                   'Set4_Brawler 1': '2 Brawler',
                   'Set4_Brawler 2': '4 Brawler',
                   'Set4_Brawler 3': '6 Brawler',
                   'Set4_Brawler 4': '8 Brawler',
                   'Cultist 1': '3 Cultist',
                   'Cultist 2': '6 Cultist',
                   'Cultist 3': '9 Cultist',
                   'Set4_Dazzler 1': '2 Dazzler',
                   'Set4_Dazzler 2': '4 Dazzler',
                   'Divine 1': '2 Divine',
                   'Divine 2': '4 Divine',
                   'Divine 3': '6 Divine',
                   'Divine 4': '8 Divine',
                   'Duelist 1': '2 Duelist',
                   'Duelist 2': '4 Duelist',
                   'Duelist 3': '6 Duelist',
                   'Duelist 4': '8 Duelist',
                   'Dusk 1': '2 Dusk',
                   'Dusk 2': '4 Dusk',
                   'Dusk 3': '6 Dusk',
                   'Set4_Elderwood 1': '3 Elderwood',
                   'Set4_Elderwood 2': '6 Elderwood',
                   'Set4_Elderwood 3': '9 Elderwood',
                   'Emperor 1': '1 Emperor',
                   'Set4_Enlightened 1': '2 Enlightened',
                   'Set4_Enlightened 2': '4 Enlightened',
                   'Set4_Enlightened 3': '6 Enlightened',
                   'Set4_Exile 1': '1 Exile',
                   'Set4_Exile 2': '2 Exile',
                   'Fortune 1': '3 Fortune',
                   'Fortune 2': '6 Fortune',
                   'Hunter 1': '2 Hunter',
                   'Hunter 2': '3 Hunter',
                   'Hunter 3': '4 Hunter',
                   'Hunter 4': '5 Hunter',
                   'Keeper 1': '2 Keeper',
                   'Keeper 2': '4 Keeper',
                   'Keeper 3': '6 Keeper',
                   'Set4_Mage 1': '3 Mage',
                   'Set4_Mage 2': '6 Mage',
                   'Set4_Mage 3': '9 Mage',
                   'Moonlight 1': '3 Moonlight',
                   'Set4_Mystic 1': '2 Mystic',
                   'Set4_Mystic 2': '4 Mystic',
                   'Set4_Mystic 3': '6 Mystic',
                   'Set4_Ninja 1': '1 Ninja',
                   'Set4_Ninja 2': '4 Ninja',
                   'Set4_Shade 1': '2 Shade',
                   'Set4_Shade 2': '3 Shade',
                   'Set4_Shade 3': '4 Shade',
                   'Sharpshooter 1': '2 Sharpshooter',
                   'Sharpshooter 2': '4 Sharpshooter',
                   'Sharpshooter 3': '6 Sharpshooter',
                   'Set4_Spirit 1': '2 Spirit',
                   'Set4_Spirit 2': '4 Spirit',
                   'Boss 1': '1 The Boss',
                   'Set4_Tormented 1': '1 Tormented',
                   'Set4_Vanguard 1': '2 Vanguard',
                   'Set4_Vanguard 2': '4 Vanguard',
                   'Set4_Vanguard 3': '6 Vanguard',
                   'Warlord 1': '3 Warlord',
                   'Warlord 2': '6 Warlord',
                   'Warlord 3': '9 Warlord'}

name_decoder = {'TFT3_Ahri': 'Ahri', 'TFT3_Annie': 'Annie', 'TFT3_Ashe': 'Ashe',
                'TFT3_AurelionSol': 'Aurelion Sol', 'TFT3_Bard': 'Bard',
                'TFT3_Blitzcrank': 'Blitzcrank', 'TFT3_Cassiopeia': 'Cassiopeia',
                'TFT3_Caitlyn': 'Caitlyn', 'TFT3_ChoGath': "Cho'Gath",
                'TFT3_Darius': 'Darius', 'TFT3_Ekko': 'Ekko',
                'TFT3_Ezreal': 'Ezreal', 'TFT3_Fiora': 'Fiora',
                'TFT3_Fizz': 'Fizz', 'TFT3_Gangplank': 'Gangplank',
                'TFT3_Graves': 'Graves', 'TFT3_Gnar': 'Gnar',
                'TFT3_Illaoi': 'Illaoi', 'TFT3_Irelia': 'Irelia',
                'TFT3_Janna': 'Janna', 'TFT3_JarvanIV': 'Jarvan IV',
                'TFT3_Jayce': 'Jayce', 'TFT3_Jhin': 'Jhin', 'TFT3_Jinx': 'Jinx',
                'TFT3_KaiSa': "Kai'Sa", 'TFT3_Karma': 'Karma',
                'TFT3_KogMaw': "Kog'Maw", 'TFT3_Kassadin': 'Kassadin',
                'TFT3_Kayle': 'Kayle', 'TFT3_KhaZix': "Kha'Zix",
                'TFT3_Leona': 'Leona', 'TFT3_Lucian': 'Lucian',
                'TFT3_Lulu': 'Lulu', 'TFT3_Lux': 'Lux',
                'TFT3_Malphite': 'Malphite', 'TFT3_MasterYi': 'Master Yi',
                'TFT3_MissFortune': 'Miss Fortune',
                'TFT3_Mordekaiser': 'Mordekaiser', 'TFT3_Nautilus': 'Nautilus',
                'TFT3_Neeko': 'Neeko', 'TFT3_Nocturne': 'Nocturne',
                'TFT3_Poppy': 'Poppy', 'TFT3_Rakan': 'Rakan',
                'TFT3_Riven': 'Riven', 'TFT3_Rumble': 'Rumble',
                'TFT3_Shaco': 'Shaco', 'TFT3_Shen': 'Shen', 'TFT3_Sona': 'Sona',
                'TFT3_Soraka': 'Soraka', 'TFT3_Syndra': 'Syndra',
                'TFT3_Teemo': 'Teemo', 'TFT3_Thresh': 'Thresh',
                'TFT3_TwistedFate': 'Twisted Fate', 'TFT3_Urgot': 'Urgot',
                'TFT3_Vayne': 'Vayne', 'TFT3_VelKoz': "Vel'Koz",
                'TFT3_Vi': 'Vi', 'TFT3_Viktor': 'Viktor',
                'TFT3_WuKong': 'Wukong', 'TFT3_Xayah': 'Xayah',
                'TFT3_Xerath': 'Xerath', 'TFT3_XinZhao': 'Xin Zhao',
                'TFT3_Yasuo': 'Yasuo', 'TFT3_Zed': 'Zed', 'TFT3_Ziggs': 'Ziggs',
                'TFT3_Zoe': 'Zoe', 'TFT4_Aatrox': 'Aatrox',
                'TFT4_Ahri': 'Ahri', 'TFT4_Akali': 'Akali',
                'TFT4_Annie': 'Annie', 'TFT4_Aphelios': 'Aphelios',
                'TFT4_Ashe': 'Ashe', 'TFT4_Azir': 'Azir',
                'TFT4_Cassiopeia': 'Cassiopeia', 'TFT4_Diana': 'Diana',
                'TFT4_Elise': 'Elise', 'TFT4_Evelynn': 'Evelynn',
                'TFT4_Ezreal': 'Ezreal', 'TFT4_Fiora': 'Fiora',
                'TFT4_Garen': 'Garen', 'TFT4_Hecarim': 'Hecarim',
                'TFT4_Irelia': 'Irelia', 'TFT4_Janna': 'Janna',
                'TFT4_JarvanIV': 'Jarvan IV', 'TFT4_Jax': 'Jax',
                'TFT4_Jhin': 'Jhin', 'TFT4_Jinx': 'Jinx',
                'TFT4_Kalista': 'Kalista', 'TFT4_Katarina': 'Katarina',
                'TFT4_Kayn': 'Kayn', 'TFT4_Kennen': 'Kennen',
                'TFT4_Kindred': 'Kindred', 'TFT4_LeeSin': 'Lee Sin',
                'TFT4_Lillia': 'Lillia', 'TFT4_Lissandra': 'Lissandra',
                'TFT4_Lulu': 'Lulu', 'TFT4_Lux': 'Lux', 'TFT4_Maokai': 'Maokai',
                'TFT4_Morgana': 'Morgana', 'TFT4_Nami': 'Nami',
                'TFT4_Nidalee': 'Nidalee', 'TFT4_Nunu': 'Nunu & Willump',
                'TFT4_Pyke': 'Pyke', 'TFT4_Riven': 'Riven',
                'TFT4_Sejuani': 'Sejuani', 'TFT4_Sett': 'Sett',
                'TFT4_Shen': 'Shen', 'TFT4_Sylas': 'Sylas',
                'TFT4_TahmKench': 'Tahm Kench', 'TFT4_Talon': 'Talon',
                'TFT4_Teemo': 'Teemo', 'TFT4_Thresh': 'Thresh',
                'TFT4_TwistedFate': 'Twisted Fate', 'TFT4_Vayne': 'Vayne',
                'TFT4_Veigar': 'Veigar', 'TFT4_Vi': 'Vi',
                'TFT4_Warwick': 'Warwick', 'TFT4_Wukong': 'Wukong',
                'TFT4_XinZhao': 'Xin Zhao', 'TFT4_Yasuo': 'Yasuo',
                'TFT4_Yone': 'Yone', 'TFT4_Yuumi': 'Yuumi',
                'TFT4_Zed': 'Zed', 'TFT4_Zilean': 'Zilean'}

region_decoder = {"BR":"br1", "EUNE":"eun1", "EUW":"euw1", "JP":"jp1", "KR":"kr",
                  "LAN":"la1", "LAS":"la2", "NA":"na1", "OCE":"oc1", "TR":"tr1", "RU":"ru"}

def create_item_decoder():
    with open("items.json") as items_file:
        items = json.load(items_file)    # List of dictionaries
        for item in items:
            item_decoder[item["id"]] = item["name"]
    return item_decoder

def create_synergy_decoder():
    with open("traits.json") as synergies_file:
        synergies = json.load(synergies_file)    # List of dictionaries
        for synergy in synergies:
            synergy_key = synergy["key"]
            synergy_name = synergy["name"]
            synergy_by_tier = synergy["sets"]
            for i in range(len(synergy_by_tier)):
                this_tier = synergy_by_tier[i]
                api_synergy_data = synergy_key + " " + str(i + 1)
                synergy_decoder[api_synergy_data] = str(this_tier["min"]) \
                                                    + " " + synergy_name
    return synergy_decoder  

def create_name_decoder():
    with open("champions.json") as names_file:
        names = json.load(names_file)    # List of dictionaries
        for name in names:
            name_decoder[name["championId"]] = name["name"]
    return name_decoder

def create_chosen_decoder():
    # Chosen is slightly different from synergy decider as it has no number
    chosen_decoder = {}
    with open("traits.json") as synergies_file:
        synergies = json.load(synergies_file)
        for synergy in synergies:
            chosen_decoder[synergy["key"]] = synergy["name"]
    return chosen_decoder


item_decoder = create_item_decoder()
name_decoder = create_name_decoder()
synergy_decoder = create_synergy_decoder()
chosen_decoder = create_chosen_decoder()


################################################################################
'''Running the Discord bot. '''
client = commands.Bot(command_prefix = '//', help_command = None)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # Set the Bot's status message (Listening to //help)
    activity = discord.Activity(name='//help', type=discord.ActivityType.listening)
    await client.change_presence(activity = activity)

################################################################################
'''
Uses dblpy's autopost feature to post guild count to top.gg every 30 minutes.
'''

class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Set this to your DBL token
        self.token = 'DBL_TOKEN'
        # Autopost will post your guild count every 30 minutes
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        print("Server count posted successfully")

def setup(bot):
    bot.add_cog(TopGG(client))

setup(client)


################################################################################
''' Basic bot commands, as well as a function to check whether any command
was run by a user or another bot. '''

def check_if_bot(ctx):
    if ctx.author.bot == True:
        print("command was used by a bot!")
        return False
    else:
        return True


@client.command()
@commands.check(check_if_bot)
async def ping(ctx):
    await ctx.send('pong!')


@client.command()
@commands.check(check_if_bot)
async def help(ctx):
    msg = "\n**//recentmatch** *[region] [summoner]* - gives the most recent TFT match for the specified summoner\n\
**//matchhistory** *[region] [summoner]* - gives a list of TFT matches for the specified summoner. Add a reaction to view detailed match info!\n\
**//tftrank** *[region] [summoner]* - gives the summoner's tft rank\n\
**//regions** - gives a list of region codes (used in other commands)\n\
**//ping** - returns pong!\n"
    
    support_server = "Join the support server to request new commands or report bugs: **https://discord.gg/ZC4m7ut**"

    embed_msg = discord.Embed(
        colour = discord.Colour.green()
        )
    embed_msg.add_field(name = "Command List", value = msg, inline = False)
    embed_msg.add_field(name = "Need more help?", value = support_server, inline = False)
    
    await(ctx.channel.send(embed = embed_msg))


################################################################################

@client.command()
@commands.check(check_if_bot)
async def regions(ctx):
    msg = "**NA**: North America\n\
**EUW**: West Europe\n\
**EUNE**: North Europe\n\
**OCE**: Oceania\n\
**KR**: Korea\n\
**BR**: Brazil\n\
**LAN**: Latin America North\n\
**LAS**: Latin America South\n\
**TR**: Turkey\n\
**RU**: Russia\n\
**JP**: Japan"
    embed_msg = discord.Embed(
        colour = discord.Colour.green()
        )
    embed_msg.add_field(name = "Region Codes", value = msg)
    await ctx.channel.send(embed = embed_msg)

    
################################################################################

    
@client.command()
@commands.check(check_if_bot)
async def recentmatch(ctx, region_code, *, summoner = None):
    await ctx.channel.trigger_typing()

    # Get region routing value
    try:
        region_route = region_decoder[region_code.upper()]
    except:
        embed_msg = discord.Embed( 
                color = discord.Colour.red()
                )
        msg = "Command format should be: //recentmatch [region code] [summoner] \n\
Use //regions to see list of correct region codes."
        embed_msg.add_field(name ="Region code used incorrectly!", value = msg)
        await ctx.channel.send(embed = embed_msg)

    # Requesting summoner's info
    puuid = get_player_puuid(summoner, region_route)
    if type(puuid) is int:
        embed_msg = discord.Embed(
            color = discord.Colour.red()
            )
        if puuid == 404:
            msg = "Invalid summoner name used."
            embed_msg.add_field(name = "Error!", value = msg)
        else:
            msg = "Status code: {}".format(puuid)
            embed_msg.add_field(name = "Riot API unresponsive!", value = msg)
        await ctx.channel.send(embed = embed_msg)
        
    # Requesting summoner's most recent match ID from puuid
    matchID = get_most_recent_matchID(puuid, region_route)
    if matchID == None:
        # There is no recent match played
        embed_msg = discord.Embed(
            title = "No recent TFT match played by {}.".format(summoner),
            color = discord.Colour.red()
            )
    else:
        # There is a recent match
        # Requesting most recent match data
        embed_msg = get_tft_match(matchID, puuid, summoner, region_route)
        
    if ctx.author.avatar != None:
        author_avatar_link = "https://cdn.discordapp.com/" + ctx.author.avatar
        embed_msg.set_author(name = ctx.author.name, \
                             icon_url = ctx.author.avatar_url)
         
    await ctx.channel.send(embed = embed_msg)
    #except:
    #    await ctx.channel.send("Data obtained from Riot is incomplete.")


################################################################################


@client.command()
@commands.check(check_if_bot)
async def matchhistory(ctx, region_code, *, summoner = None):
    user = ctx.author
    ment = user.mention    

    await ctx.channel.trigger_typing()

    # get region routing value
    try:
        region_route = region_decoder[region_code.upper()]
    except:
        embed_msg = discord.Embed( 
                color = discord.Colour.red()
                )
        msg = "Command format should be: //matchhistory [region code] [summoner] \n\
Use //regions to see list of correct region codes."
        embed_msg.add_field(name ="Region code used incorrectly!", value = msg)
        await ctx.channel.send(embed = embed_msg)

    # requesting summoner's info
    puuid = get_player_puuid(summoner, region_route)
    if type(puuid) is int:
        embed_msg = discord.Embed(
            color = discord.Colour.red()
            )
        if puuid == 404:
            msg = "Invalid summoner name used."
            embed_msg.add_field(name = "Error!", value = msg)
        else:
            msg = "Status code: {}".format(puuid)
            embed_msg.add_field(name = "Riot API unresponsive!", value = msg)
        await ctx.channel.send(embed = embed_msg)

    # requesting summoner's recent 9 match IDs from puuid
    recent_match_IDs = get_recent_matches(puuid, region_route, 9)

    # Get data for all the match IDs
    embed_msg, cache_matchdata = get_matches_data(summoner, puuid, \
                                                  recent_match_IDs, \
                                                  region_route)

    # Add more detail to the embed message
    if ctx.author.avatar != None:
        author_avatar_link = "https://cdn.discordapp.com/" + ctx.author.avatar
        embed_msg.set_author(name = ctx.author.name, \
                             icon_url = ctx.author.avatar_url)
    
    # Send the message and add the numbered emojis as reactions
    history_msg = await ctx.channel.send(embed = embed_msg)
    if cache_matchdata != None:
        await history_msg.add_reaction('1️⃣')
        await history_msg.add_reaction('2️⃣')
        await history_msg.add_reaction('3️⃣')
        await history_msg.add_reaction('4️⃣')
        await history_msg.add_reaction('5️⃣')
        await history_msg.add_reaction('6️⃣')
        await history_msg.add_reaction('7️⃣')
        await history_msg.add_reaction('8️⃣')
        await history_msg.add_reaction('9️⃣')

    # defining the anti-spam check (make sure the reaction is a
    # number emoji and it was sent by the same discord user)
    def check_msg(reaction,user):
        return reaction.message.id == history_msg.id and user == ctx.author

    # Wait for reactions for 2 minutes, in order to provide detailed match info
    end_time = time.time() + (60 * 2)
    while time.time() < end_time:
        reaction, user = await client.wait_for('reaction_add', check=check_msg)
        reactions_list = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
       
        if str(reaction.emoji) in reactions_list:
            j = reactions_list.index(str(reaction.emoji))
            
            matchinfo = cache_matchdata[j]
            placement = matchinfo.get("placement")
            galaxy = matchinfo.get("galaxy")
            level = matchinfo.get("level")
            synergies_msg = matchinfo.get("synergies")
            units_msg = matchinfo.get("units")
            queue = matchinfo.get("queue")
            
            if j in [3, 4, 5, 6, 7, 8]:
                numb = str(j + 1) + 'th'               
            elif j == 0:
                numb = '1st'
            elif j == 1:
                numb = '2nd'                
            elif j == 2:
                numb = '3rd'

            embed_msg = discord.Embed( 
                title = "{} most recent match for {}".format(numb, summoner),
                color = discord.Colour.blue()
                )
            if ctx.author.avatar != None:
                embed_msg.set_author(name = ctx.author.name, \
                             icon_url = ctx.author.avatar_url)
            game_info = "Game type: " + queue + "\n " \
                        + "Placement: " + str(placement) + "\n " \
                        + "Level: " + str(level)
            if galaxy != None:
                game_info = game_info + "\n " + "Galaxy: " + galaxy    
            embed_msg.add_field(name = "Game Info", value = game_info, inline = False)
            if synergies_msg != "":
                embed_msg.add_field(name = "Synergies", value = synergies_msg, inline = False)
            if units_msg != "":
                embed_msg.add_field(name = "Units", value = units_msg, inline = False)   
            await ctx.channel.send(embed = embed_msg)


################################################################################


@client.command()
@commands.check(check_if_bot)
async def tftrank(ctx, region_code, *, summoner = None):
    # get region routing value
    try:
        region_route = region_decoder[region_code.upper()]
    except:
        embed_msg = discord.Embed( 
                color = discord.Colour.red()
                )
        msg = "Command format should be: //tftrank [region code] [summoner] \n\
Use //regions to see list of correct region codes."
        embed_msg.add_field(name ="Region code used incorrectly!", value = msg)
        await ctx.channel.send(embed = embed_msg)
         
    #requesting summoner's info
    summonerName = summoner.replace(' ','%20')
        
    APIlink = 'https://{}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{}'.format(region_route, summonerName)
    summoner_data = requests.get(APIlink, headers = headers)

    #did the request succeed?
    riotAPI_statuscode = summoner_data.status_code
    if riotAPI_statuscode != 200:
        errorcode = riotAPI_statuscode
        embed_msg = discord.Embed(
            color = discord.Colour.red()
            )
        if errorcode == 404:
            msg = "Invalid summoner name used."
            embed_msg.add_field(name = "Error", value = msg)
        else:
            msg = "Status code: {}".format(puuid)
            embed_msg.add_field(name = "Riot API unresponsive!", value = msg)
        await ctx.channel.send(embed = embed_msg)

    #convert summoner data to useable format
    summoner_data = summoner_data.json()

    #get the summoner's userid
    userid = summoner_data.get("id")

    #get the summoner's rank info
    APIlink = f"https://{region_route}.api.riotgames.com/tft/league/v1/entries/by-summoner/{userid}"
    rankinfo = requests.get(APIlink, headers=headers)

    #convert rank data to useable format
    rankinfo = rankinfo.json()
    if rankinfo == []:
        rank = "UNRANKED"
    else:
        rankinfo = rankinfo[0]
        rank = rankinfo.get("tier") + ' ' + rankinfo.get("rank")

    summonercaps = summoner.upper()
    msg = f"{summonercaps} is {rank}"
    await ctx.channel.send(msg)


################################################################################
''' Hidden commands used for development. '''

@client.command()
@commands.check(check_if_bot)
async def myuserid(ctx):
    #get your discord user ID
    disc_userid = ctx.author.id
    user = client.get_user(disc_userid)
    ment = user.mention
    await ctx.channel.send(f"Your ID is {disc_userid}, {ment}!")

@client.command()
@commands.check(check_if_bot)
async def updatemessage(ctx, *, msg):
    # Check that the user is Helen
    print("Update message used, was it helen?:", ctx.author.id == 169930632632336384)
    if ctx.author.id == 169930632632336384:
        # Set the Bot's status message
        # Listening to {msg}
        print("Changing status to", msg)
        activity = discord.Activity(name = msg, type=discord.ActivityType.listening)
    else:
        activity = discord.Activity(name='//help', type=discord.ActivityType.listening)
    await client.change_presence(activity = activity)

    
################################################################################
''' Helper functions for running the bot's commands. '''


# Input: A summoner name.
# Output: That summoner's puuid (an identifier Riot uses for players.)
def get_player_puuid(summoner_name, region_route):    
    # requesting summoner's info
    print("Requested by summoner:", summoner_name)
    summonerName = summoner_name.replace(' ','%20')
    APIlink = 'https://{}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{}'.format(region_route, summonerName)
    summoner_data = requests.get(APIlink, headers = headers)

    # did the Riot API request succeed?
    riotAPI_statuscode = summoner_data.status_code
    if riotAPI_statuscode != 200:
        errorcode = riotAPI_statuscode
        return errorcode

    # convert summoner data to useable format
    summoner_data = summoner_data.json()
    
    # get the summoner's puuid
    puuid = summoner_data.get("puuid")
    return puuid


# Input: A summoner's puuid.
# Output: The match ID of their most recent TFT match.
def get_most_recent_matchID(puuid, region_route):
    if region_route in ["br1", "la1", "la2", "na1"]:
        host = "americas"
    elif region_route in ["eun1", "euw1", "tr1", "ru"]:
        host = "europe"
    else:
        host = "asia"
        
    APIlink = 'https://{}.api.riotgames.com/tft/match/v1/matches/by-puuid/{}/ids?count=1'.format(host, puuid)
    recent_match_ID = requests.get(APIlink, headers = headers)

    # did the request succeed?
    riotAPI_statuscode = recent_match_ID.status_code
    if riotAPI_statuscode != 200:
        errorcode = riotAPI_statuscode
        print('Riot API not reached, status code:', errorcode)

    # make the recent match ID result usable
    recent_match_ID = recent_match_ID.json()
    try:
        matchID = recent_match_ID[0]
    except IndexError:
        matchID = None
    return matchID


# Input: MatchID and a player's PUUID.
# Output: embed message to be sent by the bot
def get_tft_match(matchID, puuid, summoner, region_route):
    # get the host route
    if region_route in ["br1", "la1", "la2", "na1"]:
        host = "americas"
    elif region_route in ["eun1", "euw1", "tr1", "ru"]:
        host = "europe"
    else:
        host = "asia"
        
    API_link = "https://{}.api.riotgames.com/tft/match/v1/matches/{}".format(host, matchID)
    match_data = requests.get(API_link, headers = headers)

    # did the request succeed?
    riotAPI_statuscode = match_data.status_code
    if riotAPI_statuscode != 200:
        errorcode = riotAPI_statuscode
        print('Riot API not reached, status code:', errorcode)    

    # convert match data to useable format
    match_data = match_data.json()
    match_data = match_data.get("info")
    match_participants = match_data.get("participants")


    # save the galaxy data - if the game was not played in set 3,
    # galaxy will be None
    galaxy = match_data.get("game_variation")
    galaxy = galaxy_decoder.get(galaxy)

    #save the queue type (normal, ranked) data
    queue = match_data.get("queue_id")
    queue = queue_type_decoder.get(queue)

    # Go to the player requested
    for participant in match_participants:
        if participant.get("puuid") == puuid:
            # get final placement & level
            placement = participant.get("placement")
            level = participant.get("level")            

            # creating a list of dictionaries for player's synergy data
            list_of_synergies = participant.get("traits")
            
            # Create string to hold synergy info for bot's message
            synergies_msg = ""
            for x in range(len(list_of_synergies)):
                synergy = list_of_synergies[x]

                # if the synergy is active, append the synergy to the list 
                # of active synergies
                if synergy.get("tier_current") > 0:
                    synergy_info = str(synergy.get("name")) + ' ' \
                                   + str(synergy.get("tier_current"))
                    synergy_txt = synergy_decoder.get(synergy_info, synergy_info)
                    synergies_msg += " " + synergy_txt + ","

            # Remove the trailing comma 
            synergies_msg = synergies_msg.rstrip(",")

            # Check that synergies were found - if synergies is an empty string,
            # make it "no synergies."
            if synergies_msg == "":
                synergies_msg = "(no synergies found.)"
            
            #creating a list of dictionaries for player's unit data
            list_of_units = participant.get("units")
            
            # Create string to hold unit info for bot's message
            units_msg = ""
            for x in range(len(list_of_units)):
                unit = list_of_units[x]
                unit_id = unit.get("character_id")
                unit_tier = unit.get("tier") * ":star:"
                unit_chosen = unit.get("chosen", False)
                unit_item_ids = unit.get("items")

                # decode unit ID into unit name
                unit_name = name_decoder.get(unit_id, unit_id)
                
                # If the unit is the chosen unit, make its name bold
                if unit_chosen != False:
                    try:
                        chosen_synergy = chosen_decoder[unit_chosen]
                        unit_name = "** Chosen " + unit_name + "** (" \
                                    + chosen_synergy + ")"
                    except:
                        print("Error with chosen unit:", unit_id, \
                              "// value given:", unit_chosen, \
                              "// Match id:", matchID)
                        pass

                if len(unit_item_ids) == 0:
                    # create unit_msg without items
                    try:
                        unit_msg = unit_name + " - " + unit_tier
                    except:
                        unit_msg = "(error with unit.)"
                else:
                    # create unit_msg with items
                    try:
                        unit_msg = unit_name + " - " + unit_tier + " - "
                        for i in unit_item_ids:
                            item_name = item_decoder.get(i)
                            unit_msg = unit_msg + " " + item_name + ","
                    except:
                        unit_msg = "(error with unit.)"
                        
                #append unit_txt to units_msg
                unit_msg = unit_msg.rstrip(',')
                units_msg = units_msg + '\n' + unit_msg
                
            # Check that units were found - if units is an empty string,
            # make it "no units found."
            if units_msg == "":
                units_msg = "(no units found.)"
                
    embed_msg = discord.Embed(
        title = f"Most recent match for {summoner}.",
        colour = discord.Colour.gold()
        )
    game_info = "Game type: " + queue + "\n " \
                        + "Placement: " + str(placement) + "\n " \
                        + "Level: " + str(level)
    if galaxy != None:
        game_info = game_info + "\n " + "Galaxy: " + galaxy
    embed_msg.add_field(name = "Game Info", value = game_info, inline = False)
    embed_msg.add_field(name = "Synergies", value = synergies_msg, inline = False)
    embed_msg.add_field(name = "Units", value = units_msg, inline = False)
    return embed_msg


# Input: puuid, num (number of matches to get)
# Output: matches_IDs_list - list of the str_num most recent match IDs
def get_recent_matches(puuid, region_route, num):
    # get the host route
    if region_route in ["br1", "la1", "la2", "na1"]:
        host = "americas"
    elif region_route in ["eun1", "euw1", "tr1", "ru"]:
        host = "europe"
    else:
        host = "asia"
    str_num = str(num)
    APIlink = f'https://{host}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={str_num}'
    recent_match_IDs = requests.get(APIlink, headers = headers)

    # did the request succeed?
    riotAPI_statuscode = recent_match_IDs.status_code
    if riotAPI_statuscode != 200:
        errorcode = riotAPI_statuscode
        print(f'Riot API not reached, status code: {errorcode}')

    # make the result usable
    recent_match_IDs = recent_match_IDs.json()
    return recent_match_IDs


# Input: the player's puuid and a list of recent match IDs.
# Output: an embed message with all the recent match IDs info.
def get_matches_data(summoner, puuid, match_IDs, region_route):
    emojis_numbers_list = [":one:",":two:",":three:",":four:",":five:",":six:",":seven:",":eight:",":nine:",":keycap_ten:"]
    cache_matchdata = []
    txt_msg = ''

    # If there are no matches played, return an empty embed message
    if match_IDs == []:
        # Create the empty embed message
        embed_msg = discord.Embed(
            title = f"Match history for {summoner}.",
            colour = discord.Colour.blue(),
            description = '(No matches found.)'
            )
        return embed_msg, None

    # get the host route
    if region_route in ["br1", "la1", "la2", "na1"]:
        host = "americas"
    elif region_route in ["eun1", "euw1", "tr1", "ru"]:
        host = "europe"
    else:
        host = "asia"

    # Create the empty embed message
    embed_msg = discord.Embed(
        title = f"Match history for {summoner}.",
        colour = discord.Colour.blue()
        )

    for i in range(len(match_IDs)):
        matchID = match_IDs[i]
        emoji = emojis_numbers_list[i]

        # requesting match data
        API_link = "https://{}.api.riotgames.com/tft/match/v1/matches/{}".format(host, matchID)
        match_data = requests.get(API_link, headers = headers)
        
        # did the request succeed?
        riotAPI_statuscode = match_data.status_code
        if riotAPI_statuscode != 200:
            errorcode = riotAPI_statuscode
            print(f'Riot API not reached, status code: {riotAPI_statuscode}')

        # convert match data to useable format
        match_data = match_data.json()
        match_data = match_data.get("info")
        match_participants = match_data.get("participants")
        
        # save the queue type (normal, ranked) data
        queue = match_data.get("queue_id")
        queue = queue_type_decoder.get(queue)
        
        # save the galaxy data
        galaxy = match_data.get("game_variation")
        galaxy = galaxy_decoder.get(galaxy)

        # go to the player specified
        for participant in match_participants:           
            if participant.get("puuid") == puuid:
                # final placement & level
                placement = participant.get("placement")
                level = participant.get("level")

                # creating a list of dictionaries for player's synergy data
                list_of_synergies = participant.get("traits")

                # create synergies message
                synergies_msg = ""
                for x in range(len(list_of_synergies)):
                    synergy = list_of_synergies[x]
                    if synergy.get("tier_current") > 0:
                        synergy_info = str(synergy.get("name")) + ' ' \
                                       + str(synergy.get("tier_current"))
                        synergy_txt = synergy_decoder.get(synergy_info, synergy_info)
                        synergies_msg = synergies_msg + ' ' \
                                        + synergy_txt + ","
                synergies_msg = synergies_msg.rstrip(",")

                # creating a list of dictionaries for player's unit data
                list_of_units = participant.get("units")
        
                # create units message
                units_msg = ""
                for x in range((len(list_of_units))):
                    unit = list_of_units[x]
                    unit_id = unit.get("character_id")
                    unit_chosen = unit.get("chosen", False)
                    unit_tier = unit.get("tier") * ':star:'
                    unit_item_ids = unit.get("items")

                    #decode unit id into unit name
                    unit_name = name_decoder.get(unit_id, unit_id)
                    
                    # If the unit is the chosen unit, make its name bold
                    if unit_chosen != False:
                        try:
                            chosen_synergy = chosen_decoder[unit_chosen]
                            unit_name = "** Chosen " + unit_name + "** (" \
                                        + chosen_synergy + ")"
                        except:
                            print("Error with chosen unit:", unit_id, \
                                  "// value given:", unit_chosen, \
                                  "// Match id:", matchID)
                            pass
                        
                    if len(unit_item_ids) == 0:
                        # Create unit_txt without items
                        try:
                            unit_txt = unit_name + ' - ' + unit_tier
                        except:
                            unit_txt = "(Error with unit.)"
                    else:
                        # Create unit_txt with items
                        try:
                            unit_txt = unit_name + ' - ' + unit_tier + ' - '
                            for i in unit_item_ids:
                                item_name = item_decoder.get(i)
                                unit_txt = unit_txt + ' ' + item_name + ','
                        except:
                            unit_txt = "(Error with unit.)"
                    
                    #append unit_txt to UNITS_TXT
                    unit_txt = unit_txt.rstrip(',')
                    units_msg = units_msg + '\n' + unit_txt

                # string for the game info    
                txt_msg = '** Placement:** ' \
                          + str(placement) + '\nGame Type: ' \
                          + queue + '\nSynergies: ' + synergies_msg + '\n'

                # dictionary containing the match's info
                matchinfo = {"galaxy":galaxy,
                         "placement":placement,
                         "level":level,
                         "synergies":synergies_msg,
                         "units":units_msg,
                         "queue":queue
                         }

                #this is a list of dictionaries containing each match's info
                cache_matchdata.append(matchinfo)

                #building the match history Discord bot's message
                embed_msg.add_field(name = emoji, value = txt_msg)
                    
    return embed_msg, cache_matchdata


################################################################################
# Run discord bot w/ the discord key
client.run('DISCORD_KEY')
