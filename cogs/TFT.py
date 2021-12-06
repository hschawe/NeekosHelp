import discord
from discord.ext import commands
import requests
import json
from NeekosHelp.helpers import checks
from NeekosHelp.helpers import create_set_decoders
from NeekosHelp import keys


class TFT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.headers = keys.headers

        queue_type_decoder, name_decoder, synergy_decoder, item_decoder, region_decoder = create_set_decoders.create_set_decoders(
            "../set-info")
        self.queue_type_decoder = queue_type_decoder
        self.item_decoder = item_decoder
        self.synergy_decoder = synergy_decoder
        self.name_decoder = name_decoder
        self.region_decoder = region_decoder

    # @commands.command()
    # @commands.check(checks.check_if_bot)
    # async def tftrank(self, ctx, ):
    #     """Prints the requested players' TFT rank to Discord"""
    #
    #     # do things
    #
    #     await ctx.channel.send(msg)

    @commands.command()
    @commands.check(checks.check_if_bot)
    async def matchhistory(self, ctx, region_code, *, summoner=None):
        print("MATCHHISTORY / {} / {} / {}".format(summoner, region_code.upper(), ctx.author))
        user = ctx.author
        ment = user.mention

        # get region routing value OR send error message
        try:
            region_route = self.region_decoder[region_code.upper()]
        except:
            embed_msg = discord.Embed(
                color=discord.Colour.red()
            )
            msg = "Command format should be: //matchhistory [region code] [summoner] \n\
            Use //regions to see list of correct region codes."
            embed_msg.add_field(name="Region code used incorrectly!", value=msg)
            await ctx.channel.send(embed=embed_msg)

        if region_route in ["br1", "la1", "la2", "na1"]:
            host = "americas"
        elif region_route in ["eun1", "euw1", "tr1", "ru"]:
            host = "europe"
        else:
            host = "asia"

        # API calls to get player puuid and match IDs
        puuid = self.get_player_puuid(summoner, region_route)
        if type(puuid) is int:
            embed_msg = discord.Embed(
                color=discord.Colour.red()
            )
            if puuid == 404:
                msg = "Invalid summoner name used."
                embed_msg.add_field(name="Error!", value=msg)
            else:
                msg = "Status code: {}".format(puuid)
                embed_msg.add_field(name="Riot API unresponsive!", value=msg)
            await ctx.channel.send(embed=embed_msg)

        matchids = self.get_matchIDs(puuid, region_route, 9)

        # Check that they have any matches played
        try:
            matchID = matchids[0]
        except IndexError:
            msg = "No recent matches found for {}.".format(summoner)
            embed_msg.add_field(name="No recent matches found!", value=msg)
            await ctx.channel.send(embed=embed_msg)

        embed_msg, match_data_cache = self.get_matchhistory_embed(matchids, summoner, puuid, host)

        # Add more detail to the embed message
        if ctx.author.avatar is not None:
            embed_msg.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        # Send the matchhistory message
        await ctx.channel.send(embed=embed_msg)

    @commands.command()
    @commands.check(checks.check_if_bot)
    async def recentmatch(self, ctx, region_code, *, summoner=None):
        """Prints the most recent TFT match to Discord"""
        print("RECENTMATCH / {} / {} / {}".format(summoner, region_code.upper(), ctx.author))

        # Get correct region routing for API calls
        try:
            region_route = self.region_decoder[region_code.upper()]
        except:
            embed_msg = discord.Embed(
                color=discord.Colour.red()
            )
            msg = "Command format should be: //matchhistory [region code] [summoner] \n\
            Use //regions to see list of correct region codes."
            embed_msg.add_field(name="Region code used incorrectly!", value=msg)
            await ctx.channel.send(embed=embed_msg)

        if region_route in ["br1", "la1", "la2", "na1"]:
            host = "americas"
        elif region_route in ["eun1", "euw1", "tr1", "ru"]:
            host = "europe"
        else:
            host = "asia"

        # API calls to get player puuid and match IDs
        puuid = self.get_player_puuid(summoner, region_route)
        if type(puuid) is int:
            embed_msg = discord.Embed(
                color=discord.Colour.red()
            )
            if puuid == 404:
                msg = "Invalid summoner name used."
                embed_msg.add_field(name="Error!", value=msg)
            else:
                msg = "Status code: {}".format(puuid)
                embed_msg.add_field(name="Riot API unresponsive!", value=msg)
            await ctx.channel.send(embed=embed_msg)

        matchids = self.get_matchIDs(puuid, region_route, 1)

        try:
            matchID = matchids[0]
        except IndexError:
            msg = "No recent matches found for {}.".format(summoner)
            embed_msg.add_field(name="No recent matches found!", value=msg)
            await ctx.channel.send(embed=embed_msg)

        # Get the recent match data
        match_data, queue = self.get_tft_match_data(matchID, puuid, host)

        # Print the recent match data
        embed_msg = self.get_recentmatch_embed(match_data, summoner, queue)

        await ctx.channel.send(embed=embed_msg)

    def get_player_puuid(self, summoner_name, region_route):
        """
        Get player puuid.
            Input: A summoner name.
            Output: That summoner's puuid (an identifier Riot uses for players.)
        """
        # requesting summoner's info
        summonerName = summoner_name.replace(' ', '%20')
        APIlink = 'https://{}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{}'.format(region_route, summonerName)
        summoner_data = requests.get(APIlink, headers=self.headers)

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

    def get_matchIDs(self, puuid, region_route, amount=1):
        """
            Input: A summoner's puuid.
            Output: The match ID of their most recent TFT match.
        """
        if region_route in ["br1", "la1", "la2", "na1"]:
            host = "americas"
        elif region_route in ["eun1", "euw1", "tr1", "ru"]:
            host = "europe"
        else:
            host = "asia"

        if amount == 1:
            APIlink = 'https://{}.api.riotgames.com/tft/match/v1/matches/by-puuid/{}/ids?count=1'.format(host, puuid)
        else:
            str_num = str(amount)
            APIlink = f'https://{host}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={str_num}'

        matchIDs = requests.get(APIlink, headers=self.headers)

        # did the request succeed?
        riotAPI_statuscode = matchIDs.status_code
        if riotAPI_statuscode != 200:
            errorcode = riotAPI_statuscode
            print('Riot API not reached, status code:', errorcode)

        # make the recent match ID result usable
        matchIDs = matchIDs.json()
        return matchIDs

    def get_tft_match_data(self, matchID, puuid, host):
        """
        Gets the specific TFT match.
            Input: MatchID and a player's PUUID.
            Output: Riot JSON output, the match data of the player (participant)
        """

        API_link = "https://{}.api.riotgames.com/tft/match/v1/matches/{}".format(host, matchID)
        match_data = requests.get(API_link, headers=self.headers)

        # did the request succeed?
        riotAPI_status = match_data.status_code
        if riotAPI_status != 200:
            print('Riot API not reached, status code:', riotAPI_status)
            return riotAPI_status, None

        # convert match data to useable format
        match_data = match_data.json()
        match_data = match_data.get("info")
        match_participants = match_data.get("participants")

        # save the queue type (normal, ranked) data
        queue = match_data.get("queue_id")
        queue = self.queue_type_decoder.get(queue)

        # Go to the player requested
        for participant in match_participants:
            if participant.get("puuid") == puuid:
                return participant, queue

    def get_recentmatch_embed(self, match_data, summoner, queue):
        # get final placement & level
        placement = match_data.get("placement")
        level = match_data.get("level")

        # creating a list of dictionaries for player's synergy data
        list_of_synergies = match_data.get("traits")

        # Create string to hold synergy info for bot's message
        synergies_msg = ""
        for x in range(len(list_of_synergies)):
            synergy = list_of_synergies[x]

            # if the synergy is active, append the synergy to the list
            # of active synergies
            if synergy.get("tier_current") > 0:
                synergy_info = str(synergy.get("name")) + ' ' \
                               + str(synergy.get("tier_current"))
                synergy_txt = self.synergy_decoder.get(synergy_info, synergy_info)
                synergies_msg += " " + synergy_txt + ","

        # Remove the trailing comma
        synergies_msg = synergies_msg.rstrip(",")

        # Check that synergies were found - if synergies is an empty string,
        # make it "no synergies."
        if synergies_msg == "":
            synergies_msg = "(no synergies found.)"

        # creating a list of dictionaries for player's unit data
        list_of_units = match_data.get("units")

        # Create string to hold unit info for bot's message
        units_msg = ""
        for x in range(len(list_of_units)):
            unit = list_of_units[x]
            unit_id = unit.get("character_id")
            unit_tier = unit.get("tier") * ":star:"
            unit_item_ids = unit.get("items")

            # decode unit ID into unit name
            unit_name = self.name_decoder.get(unit_id, unit_id)

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
                        item_name = self.item_decoder.get(i, "")
                        unit_msg = unit_msg + " " + item_name + ","
                except:
                    unit_msg = "(error with unit.)"

            # append unit_txt to units_msg
            unit_msg = unit_msg.rstrip(',')
            units_msg = units_msg + '\n' + unit_msg

        # Check that units were found - if units is an empty string,
        # make it "no units found."
        if units_msg == "":
            units_msg = "(no units found.)"

        embed_msg = discord.Embed(
            title=f"Most recent match for {summoner}.",
            colour=discord.Colour.gold()
        )

        game_info = "Game type: " + queue + "\n " \
                    + "Placement: " + str(placement) + "\n " \
                    + "Level: " + str(level)

        embed_msg.add_field(name="Game Info", value=game_info, inline=False)
        embed_msg.add_field(name="Synergies", value=synergies_msg, inline=False)
        embed_msg.add_field(name="Units", value=units_msg, inline=False)

        return embed_msg

    def get_matchhistory_embed(self, matchids, summoner, puuid, host):
        emojis_numbers_list = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:",
                               ":keycap_ten:"]
        match_data_cache = []

        # Create the empty embed message
        embed_msg = discord.Embed(
            title=f"Match history for {summoner}.",
            colour=discord.Colour.blue()
        )

        for i in range(len(matchids)):
            matchID = matchids[i]
            emoji = emojis_numbers_list[i]

            # Get the match data
            match_data, queue = self.get_tft_match_data(matchID, puuid, host)

            # did the request succeed?
            if match_data is int:
                if match_data != 200:
                    print(f'Riot API not reached, status code: {match_data}')

            msg, cache = self.get_match_simple_msg(match_data, queue, puuid)
            match_data_cache.append(cache)

            embed_msg.add_field(name=emoji, value=msg)

        return embed_msg, match_data_cache

    def get_match_simple_msg(self, match_data, queue, puuid):
        # final placement & level
        placement = match_data.get("placement")
        level = match_data.get("level")

        # creating a list of dictionaries for player's synergy data
        list_of_synergies = match_data.get("traits")

        # create synergies message
        synergies_msg = ""
        for x in range(len(list_of_synergies)):
            synergy = list_of_synergies[x]
            if synergy.get("tier_current") > 0:
                synergy_info = str(synergy.get("name")) + ' ' + str(synergy.get("tier_current"))
                synergy_txt = self.synergy_decoder.get(synergy_info, synergy_info)
                synergies_msg = synergies_msg + ' ' + synergy_txt + ","
        synergies_msg = synergies_msg.rstrip(",")

        # creating a list of dictionaries for player's unit data
        list_of_units = match_data.get("units")

        # create units message
        units_msg = ""
        for x in range((len(list_of_units))):
            unit = list_of_units[x]
            unit_id = unit.get("character_id")
            unit_tier = unit.get("tier") * ':star:'
            unit_item_ids = unit.get("items")

            # decode unit id into unit name
            unit_name = self.name_decoder.get(unit_id, unit_id)

            if len(unit_item_ids) == 0:
                # Create unit_txt without items
                try:
                    unit_txt = unit_name + ' - ' + unit_tier
                except Exception as ex:
                    unit_txt = "(Error with unit.)"
                    print("(Error with unit.)", ex, puuid, unit_name, unit_tier)
            else:
                # Create unit_txt with items
                try:
                    unit_txt = unit_name + ' - ' + unit_tier + ' - '
                    for i in unit_item_ids:
                        item_name = self.item_decoder.get(i, "")
                        unit_txt = unit_txt + ' ' + item_name + ','
                except Exception as ex:
                    unit_txt = "(Error with unit.)"
                    print("(Error with unit.)", ex, puuid, unit_name, unit_tier, unit_item_ids)

            # append unit_txt to message
            unit_txt = unit_txt.rstrip(',')
            units_msg = units_msg + '\n' + unit_txt

        # string for the game info
        msg = '** Placement:** ' + str(placement) + '\nGame Type: ' + queue + '\nSynergies: ' + synergies_msg \
              + '\n'

        # dictionary containing the match's info
        cache = {"placement": placement,
                 "level": level,
                 "synergies": synergies_msg,
                 "units": units_msg,
                 "queue": queue
                 }

        return msg, cache


def setup(bot):
    bot.add_cog(TFT(bot))
