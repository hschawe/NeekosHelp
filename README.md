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
1. Riot TFT files
2. a Riot API key
3. a Discord Bot key. 

(Make sure that the last 2 remain private, don't share them with anyone else!)

1. Riot TFT files 
   * Login to https://developer.riotgames.com/ 
   * At the top bar navigate to Docs > League of Legends. 
   * Scroll down to "Data Dragon" and download the latest tar.
   * Untar these files, navigate to the data directory in the untarred files. You can choose any language, I use en_US. Copy files starting with tft-* into the NeekosHelp/set-info/ directory.
2. Riot API key
   * Same website, https://developer.riotgames.com/ 
   * Either use a development key (Riot Fist on top left, refresh the key and copy)
   * Or use an application key (you'll have to register a product with Riot)
   * Paste copied key into .env file
3. Discord Bot token
   * Go to https://discord.com/developers/applications
   * Make a New Application, then navigate to Bot on the left sidebar. Click Add Bot, then copy its Token. 
   * On the same page, scroll down from where you copied the token, turn on the "Message Content Intent" 
   * Paste token into .env file

You can (mostly) safely ignore the top.gg references in the code. The official bot is advertised on top.gg, it uses this to post the public Neeko's Help's server count to the site. 