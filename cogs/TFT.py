import asyncio
import discord
from discord.ext import commands
import requests
import json
from helpers import checks, create_decoders as decoder, helpers, talkies
import keys


class TFT(commands.Cog):
    """Class that contains commands related to TFT game."""

    def __init__(self, bot):
        self.bot = bot
        self.headers = keys.headers

    @commands.hybrid_command()
    @commands.check(checks.check_if_bot)
    async def regions(self, ctx):
        """Print bot's accepted region codes to Discord"""
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
        **JP**: Japan\n\
        **PH**: Philippines\n\
        **SG**: Singapore\n\
        **TH**: Thailand\n\
        **TW**: Taiwan\n\
        **VN**: Vietnam\n"

        embed_msg = discord.Embed(
            colour=discord.Colour.green()
        )
        embed_msg.add_field(name="Region Codes", value=msg)
        await ctx.channel.send(embed=embed_msg)

    @commands.hybrid_command()
    @commands.check(checks.check_if_bot)
    async def tftrank(self, ctx, region_code=None, *, summoner=None):
        """Prints the requested players' TFT rank to Discord"""
        print(f"TFTRANK / {str(summoner)} / {str(region_code)} / {ctx.author}")
        if (region_code is None) or (summoner is None):
            info_msg = "Command format should be: //tftrank [region code] [summoner]\n Use //regions to see list " \
                       "of correct region codes. "
            embed_msg = discord.Embed(
                colour=discord.Colour.red()
            )
            embed_msg.add_field(
                name="Incorrect command format!", value=info_msg)
        else:
            embed_msg = self.get_player_tft_rank(region_code, summoner)
        await ctx.channel.send(embed=embed_msg)

    @commands.hybrid_command()
    @commands.check(checks.check_if_bot)
    async def matchhistory(self, ctx, region_code=None, *, summoner=None):
        """Prints the requested player's TFT match history (prev. 9 games) to Discord"""
        print(
            f"MATCHHISTORY / {str(summoner)} / {str(region_code)} / {ctx.author}")

        if (region_code is None) or (summoner is None):
            info_msg = "Command format should be: //matchhistory [region code] [summoner]\n Use //regions to see list " \
                       "of correct region codes. "
            embed_msg = discord.Embed(
                colour=discord.Colour.red()
            )
            embed_msg.add_field(
                name="Incorrect command format!", value=info_msg)
            await ctx.channel.send(embed=embed_msg)
        else:
            # get region routing value OR send error message
            try:
                region_route = decoder.region[region_code.upper()]
            except KeyError:
                embed_msg = discord.Embed(
                    color=discord.Colour.red()
                )
                msg = "Command format should be: //matchhistory [region code] [summoner] \n\
                Use //regions to see list of correct region codes."
                embed_msg.add_field(
                    name="Incorrect region code used!", value=msg)
                await ctx.channel.send(embed=embed_msg)

            if region_route in ["br1", "la1", "la2", "na1"]:
                host = "americas"
            elif region_route in ["eun1", "euw1", "tr1", "ru"]:
                host = "europe"
            elif region_route in ["oc1", "ph2", "sg2", "th2", "tw2", "vn2"]:
                host = "sea"
            else:
                host = "asia"

            # API calls to get player puuid and match IDs
            puuid = self.get_player_puuid(summoner, region_route)
            if isinstance(puuid, int):
                embed_msg = discord.Embed(
                    color=discord.Colour.red()
                )
                if puuid == 404:
                    msg = "Invalid summoner name used."
                    embed_msg.add_field(name="Error!", value=msg)
                else:
                    msg = f"Status code: {puuid}"
                    embed_msg.add_field(
                        name="Riot API unresponsive!", value=msg)
                await ctx.channel.send(embed=embed_msg)

            match_ids = self.get_match_ids(puuid, region_route, 9)

            # Check that they have any matches played
            try:
                matchID = match_ids[0]
            except IndexError:
                msg = f"No recent matches found for {summoner}."
                embed_msg.add_field(name="No recent matches found!", value=msg)
                await ctx.channel.send(embed=embed_msg)

            embed_msg, match_data_cache = self.get_matchhistory_embed(
                match_ids, summoner, puuid, host)

            # Add more detail to the embed message
            if ctx.author.avatar is not None:
                embed_msg.set_author(name=ctx.author.name,
                                     icon_url=ctx.author.avatar)

            # Send the message and add the numbered emojis as reactions
            history_msg = await ctx.channel.send(embed=embed_msg)
            if match_data_cache is not None:
                await history_msg.add_reaction('1️⃣')
                await history_msg.add_reaction('2️⃣')
                await history_msg.add_reaction('3️⃣')
                await history_msg.add_reaction('4️⃣')
                await history_msg.add_reaction('5️⃣')
                await history_msg.add_reaction('6️⃣')
                await history_msg.add_reaction('7️⃣')
                await history_msg.add_reaction('8️⃣')
                await history_msg.add_reaction('9️⃣')

            await self.wait_for_interaction(ctx, history_msg, match_data_cache, summoner)

    @commands.hybrid_command()
    @commands.check(checks.check_if_bot)
    async def recentmatch(self, ctx, region_code=None, *, summoner=None):
        """Prints the most recent TFT match to Discord"""
        print(
            f"RECENTMATCH / {str(summoner)} / {str(region_code)} / {ctx.author}")
        if (region_code is None) or (summoner is None):
            info_msg = "Command format should be: //recentmatch [region code] [summoner]\n Use //regions to see list " \
                       "of correct region codes. "
            embed_msg = discord.Embed(
                colour=discord.Colour.red()
            )
            embed_msg.add_field(
                name="Incorrect command format!", value=info_msg)
            await ctx.channel.send(embed=embed_msg)
        else:
            # Get correct region routing for API calls
            try:
                region_route = decoder.region[region_code.upper()]
            except KeyError:
                embed_msg = discord.Embed(
                    color=discord.Colour.red()
                )
                msg = "Command format should be: //matchhistory [region code] [summoner] \n\
                Use //regions to see list of correct region codes."
                embed_msg.add_field(
                    name="Incorrect region code used!", value=msg)
                await ctx.channel.send(embed=embed_msg)

            if region_route in ["br1", "la1", "la2", "na1"]:
                host = "americas"
            elif region_route in ["eun1", "euw1", "tr1", "ru"]:
                host = "europe"
            elif region_route in ["oc1", "ph2", "sg2", "th2", "tw2", "vn2"]:
                host = "sea"
            else:
                host = "asia"

            # API calls to get player puuid and match IDs
            puuid = self.get_player_puuid(summoner, region_route)
            if isinstance(puuid, int):
                embed_msg = discord.Embed(
                    color=discord.Colour.red()
                )
                if puuid == 404:
                    msg = "Invalid summoner name used."
                    embed_msg.add_field(name="Error!", value=msg)
                else:
                    msg = f"Status code: {puuid}"
                    embed_msg.add_field(
                        name="Riot API unresponsive!", value=msg)
                await ctx.channel.send(embed=embed_msg)

            match_ids = self.get_match_ids(puuid, region_route, 1)

            try:
                matchID = match_ids[0]
            except IndexError:
                msg = f"No recent matches found for {summoner}."
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
        summoner_name = summoner_name.replace(' ', '%20')
        api_link = f'https://{region_route}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{summoner_name}'
        summoner_data = requests.get(api_link, headers=self.headers)

        # did the Riot API request succeed?
        riot_api_status_code = summoner_data.status_code
        if riot_api_status_code != 200:
            errorcode = riot_api_status_code
            return errorcode

        # convert summoner data to useable format
        summoner_data = summoner_data.json()

        # get the summoner's puuid
        puuid = summoner_data.get("puuid")

        return puuid

    def get_match_ids(self, puuid, region_route, amount=1):
        """
            Input: A summoner's puuid.
            Output: The match ID of their most recent TFT match.
        """
        if region_route in ["br1", "la1", "la2", "na1"]:
            host = "americas"
        elif region_route in ["eun1", "euw1", "tr1", "ru"]:
            host = "europe"
        elif region_route in ["oc1", "ph2", "sg2", "th2", "tw2", "vn2"]:
            host = "sea"
        else:
            host = "asia"

        if amount == 1:
            api_link = f'https://{host}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=1'
        else:
            str_num = str(amount)
            api_link = f'https://{host}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={str_num}'

        match_ids = requests.get(api_link, headers=self.headers)

        # did the request succeed?
        riot_api_status_code = match_ids.status_code
        if riot_api_status_code != 200:
            errorcode = riot_api_status_code
            print('Riot API not reached, status code:', errorcode)

        # make the recent match ID result usable
        match_ids = match_ids.json()
        return match_ids

    def get_tft_match_data(self, matchID, puuid, host):
        """
        Gets the specific TFT match.
            Input: MatchID and a player's PUUID.
            Output: Riot JSON output, the match data of the player (participant)
        """

        api_link = f"https://{host}.api.riotgames.com/tft/match/v1/matches/{matchID}"
        match_data = requests.get(api_link, headers=self.headers)
        # did the request succeed?
        riot_api_status = match_data.status_code
        if riot_api_status != 200:
            print('Riot API not reached, status code:', riot_api_status)
            return riot_api_status, None

        # convert match data to useable format
        match_data = match_data.json()
        match_data = match_data.get("info")
        match_participants = match_data.get("participants")

        # save the queue type (normal, ranked) data
        queue = match_data.get("tft_game_type")
        queue = decoder.game_types.get(queue)
        queue = queue or 'Not Available'

        # Go to the player requested
        for participant in match_participants:
            if participant.get("puuid") == puuid:
                return participant, queue

    def get_recentmatch_embed(self, match_data, summoner, queue):
        """Creates embed message for recentmatch response."""
        api_placement = match_data.get("placement")
        formatted_placement = helpers.get_true_placement(
            queue, match_data.get("placement"))
        level = match_data.get("level")

        # Format traits for response
        traits = helpers.get_player_traits_from_match(match_data)
        trait_messages = []
        for _, trait in traits.items():
            if trait['tier_current'] > 0:
                trait_messages.append(
                    str(trait['num_units']) + ' ' + trait['name'] + ', ')
        trait_msg = ''.join(trait_messages)
        trait_msg = trait_msg.rstrip(", ")
        if trait_msg == "":
            trait_msg = "(No synergies found.)"

        # Format units for response
        units = helpers.get_player_units_from_match(match_data)
        unit_messages = []
        for _, unit in units.items():
            temp_msg = "*" + unit["name"] + "* - " + \
                (unit["tier"] * ":star:") + " | " + \
                decoder.cost[unit["cost"]] + "\n"
            if len(unit["items"]) > 0:
                items = helpers.get_unit_items(unit)
                item_msg = '[ '
                for _, item in items.items():
                    item_msg = item_msg + item["name"] + ', '
                item_msg = item_msg.rstrip(", ")
                temp_msg = temp_msg + item_msg + ' ]\n\n'
            else:
                temp_msg = temp_msg + "\n"
            unit_messages.append(temp_msg)
        units_msg = ''.join(unit_messages)

        embed_msg = discord.Embed(
            title=f"Most recent match for {summoner}.",
        )

        if (api_placement == 1) or (formatted_placement == 1):
            embed_msg.colour = discord.Colour.gold()
        elif (api_placement == 2) or (formatted_placement == 2):
            embed_msg.colour = discord.Colour.light_gray()
        elif api_placement == 3:
            embed_msg.colour = discord.Colour.dark_orange()
        elif api_placement <= 4:
            embed_msg.colour = discord.Colour.dark_theme()
        else:
            embed_msg.colour = discord.Colour.red()

        game_info = "Game type: " + queue + "\n " \
                    + "Placement: " + str(formatted_placement) + "\n " \
                    + "Level: " + str(level)

        embed_msg.add_field(name="Game Info", value=game_info, inline=False)
        embed_msg.add_field(name="Synergies", value=trait_msg, inline=False)
        embed_msg.add_field(name="Units", value=units_msg, inline=False)
        if (api_placement == 1) or (formatted_placement == 1):
            embed_msg.add_field(name="Neeko says...",
                                value=talkies.get_excited_line(), inline=False)
        elif api_placement > 4:
            embed_msg.add_field(name="Neeko says...",
                                value=talkies.get_sad_line(), inline=False)

        return embed_msg

    def get_matchhistory_embed(self, match_ids, summoner, puuid, host):
        """Created embed message for matchhistory response."""
        emojis_numbers_list = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:",
                               ":keycap_ten:"]
        match_data_cache = []

        # Create the empty embed message
        embed_msg = discord.Embed(
            title=f"Match history for {summoner}.",
            colour=discord.Colour.blue()
        )

        for i, match_id in enumerate(match_ids):
            emoji = emojis_numbers_list[i]

            # Get the match data
            match_data, queue = self.get_tft_match_data(match_id, puuid, host)

            # did the request succeed?
            if match_data is int:
                if match_data != 200:
                    print(f'Riot API not reached, status code: {match_data}')

            msg = self.get_match_simple_msg(match_data, queue, puuid)
            match_data_cached = {"match_data": match_data, "queue": queue}
            match_data_cache.append(match_data_cached)

            embed_msg.add_field(name=emoji, value=msg)

        return embed_msg, match_data_cache

    def get_match_simple_msg(self, match_data, queue, puuid):
        """Creates embed message for simple match response."""
        formatted_placement = helpers.get_true_placement(
            queue, match_data.get("placement"))

        traits = helpers.get_player_traits_from_match(match_data)
        trait_messages = []
        for _, trait in traits.items():
            if trait['tier_current'] > 0:
                trait_messages.append(
                    str(trait['num_units']) + ' ' + trait['name'] + ', ')
        trait_msg = ''.join(trait_messages)
        trait_msg = trait_msg.rstrip(", ")
        if trait_msg == "":
            trait_msg = "(No synergies found.)"

        msg = '** Placement:** ' + str(formatted_placement) + '\nGame Type: ' + queue + '\nSynergies:\n ' + trait_msg \
              + '\n'

        return msg

    async def wait_for_interaction(self, ctx, history_msg, match_data_cache, summoner, reactions_list=['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']):
        """Waits for an emoji interaction from a command."""
        def check_msg(reaction, user):
            return reaction.message.id == history_msg.id and user == ctx.author

        try:
            # Wait for reactions for 2 mins, check that the reaction is on the right message
            reaction, _ = await self.bot.wait_for('reaction_add', check=check_msg, timeout=120)
        except asyncio.TimeoutError:
            await history_msg.clear_reaction('1️⃣')
            await history_msg.clear_reaction('2️⃣')
            await history_msg.clear_reaction('3️⃣')
            await history_msg.clear_reaction('4️⃣')
            await history_msg.clear_reaction('5️⃣')
            await history_msg.clear_reaction('6️⃣')
            await history_msg.clear_reaction('7️⃣')
            await history_msg.clear_reaction('8️⃣')
            await history_msg.clear_reaction('9️⃣')
            print("TIMEOUT")
        else:
            if str(reaction.emoji) in reactions_list:
                j = reactions_list.index(str(reaction.emoji))

                match_info = match_data_cache[j]
                embed_msg = self.get_recentmatch_embed(
                    match_info['match_data'], summoner, match_info['queue'])
                numb = ''
                if j in [3, 4, 5, 6, 7, 8]:
                    numb = str(j + 1) + 'th'
                elif j == 0:
                    numb = '1st'
                elif j == 1:
                    numb = '2nd'
                elif j == 2:
                    numb = '3rd'
                embed_msg.title = f"{numb} most recent match for {summoner}"

                await ctx.channel.send(embed=embed_msg)

                # Run again so we can handle multiple reactions
                # Remove this reaction from the list, so we don't return this match again
                reactions_list[j] = None
            await self.wait_for_interaction(ctx, history_msg, match_data_cache, summoner, reactions_list)

    def get_player_tft_rank(self, region_code, summoner):
        """Returns the summoner's TFT rank as a Discord.py Embed object"""
        # get region routing value
        try:
            region_route = decoder.region[region_code.upper()]
        except KeyError:
            embed_msg = discord.Embed(
                color=discord.Colour.red()
            )
            msg = "Command format should be: //tftrank [region code] [summoner] \n\
        Use //regions to see list of correct region codes."
            embed_msg.add_field(
                name="Region code used incorrectly!", value=msg)
            return embed_msg

        # requesting summoner's info
        summoner_name = summoner.replace(' ', '%20')

        api_link = f'https://{region_route}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{summoner_name}'
        summoner_data = requests.get(api_link, headers=self.headers)

        # did the request succeed?
        riot_api_status = summoner_data.status_code
        if riot_api_status != 200:
            embed_msg = discord.Embed(
                color=discord.Colour.red()
            )
            if riot_api_status == 404:
                msg = "Invalid summoner name used."
                embed_msg.add_field(name="Error", value=msg)
            else:
                msg = f"Error status code: {riot_api_status}"
                embed_msg.add_field(name="Riot API unresponsive!", value=msg)
            return embed_msg

        # Convert summoner data to useable format
        summoner_data = summoner_data.json()

        # Get the summoner's userid
        userid = summoner_data.get("id")

        # Get the summoner's rank info
        api_link = f"https://{region_route}.api.riotgames.com/tft/league/v1/entries/by-summoner/{userid}"
        ranks_info = requests.get(api_link, headers=self.headers)

        # Convert rank data to usable format
        summoner = summoner_data["name"]
        ranks_info = ranks_info.json()
        embed_msg = discord.Embed(
            color=discord.Colour.blue()
        )
        embed_msg.title = f"Rank info for {summoner}."
        if ranks_info is []:
            msg = f"{summoner} is Unranked."
            embed_msg.add_field(value=msg)
        else:
            for rank_info in ranks_info:
                queue = rank_info["queueType"]
                if queue == "RANKED_TFT":
                    tier = rank_info.get("tier")
                    tier = tier.capitalize()
                    rank = rank_info.get("rank")
                    wins = rank_info.get("wins")
                    lpoints = rank_info.get("leaguePoints")
                    rank_msg = f"{tier} {rank} {str(lpoints)} LP, with {str(wins)} wins."
                    embed_msg.add_field(name="Ranked TFT",
                                        value=rank_msg, inline=False)
                elif queue == "RANKED_TFT_TURBO":
                    tier = rank_info.get("ratedTier")
                    if tier == "ORANGE":
                        tier = "Hyper"
                    tier = tier.capitalize()
                    lpoints = rank_info.get("ratedRating")
                    wins = rank_info.get("wins")
                    rank_msg = f"{tier} {str(lpoints)} LP, with {str(wins)} wins."
                    embed_msg.add_field(
                        name="HyperRoll", value=rank_msg, inline=False)
        return embed_msg


async def setup(bot):
    """Discordpy cog setup"""
    await bot.add_cog(TFT(bot))
