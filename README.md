# NeekosHelp
Discord Bot to share Teamfight Tactics match history with friends! Neeko's Help is publicly available to be added to your Discord server at https://top.gg/bot/703654421074018354 

## Commands
Neeko's Help uses double slashes (//) as the prefix for every command. 

### //recentmatch [region code] [summoner]
Returns the specified summoner's most recent TFT match. Displays synergies, units, and items used. 

<img src="https://i.ibb.co/TmBPKgp/recentmatch.png">


### //matchhistory [region code] [summoner]
Returns the specified user's 10 most recent games. On the matchhistory message, the user can also add a reaction (numbered 1-10) in order to see that specific match's info.

<img src="https://i.ibb.co/SX88pXf/matchhistory-1.png"> 
<div>
<img src="https://i.ibb.co/hs2NK3J/matchhistory-2.png">
</div>

### //tftrank [region code] [summoner]
Returns the TFT rank for the specified summoner.

### Miscellaneous Commands
<ul>
  <li><b>//ping</b> - Returns pong!</li>
  <li><b>//help</b> - Returns a list of all bot commands.</li>
  <li><b>//regions</b> - Returns a list of region codes used in other TFT commands.</li>
</ul>


## How to set up your own bot

Setup a python development environment :)

In the root directory of this project create a .env file that looks like:
```
# .env
DISCORD_TOKEN={DISCORD API KEY FROM INSTRUCTIONS BELOW}
RIOT_TOKEN={RIOT API KEY FROM INSTRUCTIONS BELOW}
```

You'll need 3 things:
* Riot TFT files
* a Riot API key
* a Discord Bot key. 

(Make sure that the last 2 remain private, don't share them with anyone else!)

Riot TFT files & API key: navigate to https://developer.riotgames.com/ and login. To get the TFT files, use the top Docs bar and navigate to Teamfight Tactics section. Scroll down to Static Data and download the files under Current Set. Place these extracted json files (champions, items, and traits) in the same folder as your bot .py file. Now you will get an API key. Click APIS on the top bar, and run any API request (I recommend running LOL-STATUS-V3 because you won't need to input any extra info). After the command is run, copy the entire Request Headers surrounded by curly braces. Paste this over {'HEADER_GOES_HERE'} in line 10 of the main file.

Discord Bot token: Obtained on discord developer portal, login and navigate to Applications on the left sidebar. At the top, click New Application, then navigate to Bot on the left sidebar. Click Add Bot, then copy its Token. Paste this token (in single quotes) in parenthesis to replace 'DISCORD_KEY' on line 1024 of the main file.

Another note: Line 323 uses a key from top.gg to post the public Neeko's Help's server count to top.gg. You don't need to mess with this.
