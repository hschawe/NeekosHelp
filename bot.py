#discord_tftmatchesbot_public.py
import os
import requests
import time
import json
import discord
from discord.ext import commands
import dbl
import create_set_decoders
import neekokeys

# Header for a Riot API request.
global headers
headers = neekokeys.headers

# Discord bot key
discord_bot_key = neekokeys.discord_bot_key


# Create TFT info decoders (dictionaries)
'''  Relevant information about the past and current TFT sets.
    (set 3 and onward.)

    Create dictionaries to convert API-retrieved data to readable data (item names,
    synergy names, etc.).
'''

global queue_type_decoder
global item_decoder
global synergy_decoder
global name_decoder
global chosen_decoder
global region_decoder

region_decoder = {"BR":"br1", "EUNE":"eun1", "EUW":"euw1", "JP":"jp1", "KR":"kr",
                  "LAN":"la1", "LAS":"la2", "NA":"na1", "OCE":"oc1", "TR":"tr1", "RU":"ru"}

# Create dicts
rootdir = "../set-info"
queue_type_decoder, name_decoder, synergy_decoder, item_decoder = create_set_decoders.main(rootdir)


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
        self.token = neekokeys.topgg_token
        # Autopost will post your guild count every 30 minutes
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        print("Server count posted successfully")

def setup(bot):
    if hasattr(neekokeys, 'topgg_token'):
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
    print("RECENTMATCH / {} / {} / {}".format(summoner, region_code.upper(), ctx.author))
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
    print("MATCHHISTORY / {} / {} / {}".format(summoner, region_code.upper(), ctx.author))
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
    print("TFTRANK / {} / {} / {}".format(summoner, region_code.upper(), ctx.author))
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
    ment = ctx.author.mention
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
    await client.change_presence(activity = activity)

    
################################################################################
''' Helper functions for running the bot's commands. '''


# Input: A summoner name.
# Output: That summoner's puuid (an identifier Riot uses for players.)
def get_player_puuid(summoner_name, region_route):    
    # requesting summoner's info
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
                        print("Error -> Line543:", summoner, unit_name, unit_tier)
                        unit_msg = "(error with unit.)"
                else:
                    # create unit_msg with items
                    try:
                        unit_msg = unit_name + " - " + unit_tier + " - "
                        for i in unit_item_ids:
                            item_name = item_decoder.get(i, "")
                            unit_msg = unit_msg + " " + item_name + ","
                    except:
                        print("Error -> Line553:", summoner, unit_name, unit_tier, unit_item_ids)
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
                            print("Error -> Line712", summoner, unit_name, unit_tier)
                    else:
                        # Create unit_txt with items
                        try:
                            unit_txt = unit_name + ' - ' + unit_tier + ' - '
                            for i in unit_item_ids:
                                item_name = item_decoder.get(i, "")
                                unit_txt = unit_txt + ' ' + item_name + ','
                        except:
                            unit_txt = "(Error with unit.)"
                            print("Error -> Line722", summoner, unit_name, unit_tier, unit_item_ids)
                    
                    #append unit_txt to UNITS_TXT
                    unit_txt = unit_txt.rstrip(',')
                    units_msg = units_msg + '\n' + unit_txt

                # string for the game info    
                txt_msg = '** Placement:** ' \
                          + str(placement) + '\nGame Type: ' \
                          + queue + '\nSynergies: ' + synergies_msg + '\n'

                # dictionary containing the match's info
                matchinfo = {"placement":placement,
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
client.run(discord_bot_key)
