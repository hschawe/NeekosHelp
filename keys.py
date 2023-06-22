import os
from dotenv import load_dotenv

load_dotenv()
# Riot Developer headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": os.getenv('RIOT_TOKEN')
}

# Discord bot key
discord_bot_key = os.getenv('DISCORD_TOKEN')

# Top.gg key
# Discord bot key
topgg_token = os.getenv('TOPGG_KEY')

#Prod or Test environment
environment = os.getenv('ENVIRONMENT')

