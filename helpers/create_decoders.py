import json
import os

SET_INFO_DIR = 'set-info'

queue_type = {1090: "Normal", 1100: "Ranked", 1110: "TFT Tutorial", 1130: "Hyper Roll", 1150: "Double Up"}
game_types = {"pairs": "Double Up", "standard": "Ranked", "normal": "Normal", "turbo": "Hyper Roll"}
region = {"BR": "br1", "EUNE": "eun1", "EUN": "eun1", "EUW": "euw1", "JP": "jp1", "KR": "kr",
          "LAN": "la1", "LAS": "la2", "NA": "na1", "OCE": "oc1", "TR": "tr1", "RU": "ru", "PH": "ph2",
          "SG": "sg2", "TH": "th2", "TW": "tw2", "VN": "vn2" }
cost = {0: '1 Cost', 1:'2 Cost', 2:'3 Cost',4:'4 Cost',6:'5 Cost',9:'Summon',99:''}

def create_item(f):
    temp = {}
    with open(f) as items_file:
        items = json.load(items_file)  # List of dictionaries
        for key, item in items["data"].items():
            temp[item["id"]] = item["name"]
    return temp


def create_synergy(f):
    temp = {}
    with open(f) as synergies_file:
        synergies = json.load(synergies_file)  # List of dictionaries
        for synergy in synergies['data']:
            synergy_key = synergy
            synergy_name = synergies['data'][synergy_key]['name']
            temp[synergy_key] = synergy_name
    return temp


def create_champion(f):
    temp = {}
    with open(f) as names_file:
        names = json.load(names_file)  # List of dictionaries
        for name in names['data']:
            champ_name = names['data'][name]["name"]
            id = names['data'][name]["id"].lower()
            temp[id] = champ_name
    return temp

items = create_item(os.path.join(SET_INFO_DIR, "tft-item.json"))
traits = create_synergy(os.path.join(SET_INFO_DIR, "tft-trait.json"))
units = create_champion(os.path.join(SET_INFO_DIR, "tft-champion.json"))
