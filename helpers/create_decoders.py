import json
import os

SET_INFO_DIR = 'set-info'

queue_type = {1090: "Normal", 1100: "Ranked",
              1110: "TFT Tutorial", 1130: "Hyper Roll", 1150: "Double Up"}
game_types = {"pairs": "Double Up", "standard": "Ranked",
              "normal": "Normal", "turbo": "Hyper Roll"}
region = {"BR": "br1", "EUNE": "eun1", "EUN": "eun1", "EUW": "euw1", "JP": "jp1", "KR": "kr",
          "LAN": "la1", "LAS": "la2", "NA": "na1", "OCE": "oc1", "TR": "tr1", "RU": "ru", "PH": "ph2",
          "SG": "sg2", "TH": "th2", "TW": "tw2", "VN": "vn2"}
cost = {0: '1 Cost', 1: '2 Cost', 2: '3 Cost',
        4: '4 Cost', 6: '5 Cost', 9: 'Summon', 99: ''}


def create_item(riot_fpath, custom_fpath):
    """Function that reads item dragon data json file and turns it into a usable dict."""
    temp = {}
    with open(riot_fpath, encoding="utf8") as items_file:
        game_items = json.load(items_file)  # List of dictionaries
        for key, item in game_items["data"].items():
            temp[item["id"]] = item["name"]

    with open(custom_fpath, encoding="utf8") as custom_items_file:
        custom_items = json.load(custom_items_file)
        temp.update(custom_items)
    return temp


def create_synergy(riot_fpath, custom_fpath):
    """Function that reads traits dragon data json file and turns it into a usable dict."""
    temp = {}
    with open(riot_fpath, encoding="utf8") as synergies_file:
        synergies = json.load(synergies_file)  # List of dictionaries
        for synergy in synergies['data']:
            synergy_key = synergy
            synergy_name = synergies['data'][synergy_key]['name']
            temp[synergy_key] = synergy_name

    with open(custom_fpath, encoding="utf8") as custom_traits_file:
        custom_traits = json.load(custom_traits_file)
        temp.update(custom_traits)

    return temp


def create_champion(riot_fpath, custom_fpath):
    """Function that reads units dragon data json file and turns it into a usable dict."""
    temp = {}
    with open(riot_fpath, encoding="utf8") as names_file:
        names = json.load(names_file)  # List of dictionaries
        for name in names['data']:
            champ_name = names['data'][name]["name"]
            champ_id = names['data'][name]["id"].lower()
            temp[champ_id] = champ_name

    with open(custom_fpath, encoding="utf8") as custom_names_file:
        custom_names = json.load(custom_names_file)
        temp.update(custom_names)

    return temp


def create_augment(riot_fpath, custom_fpath):
    """Function that reads augments dragon data json file and turns it into a usable dict."""
    temp = {}
    with open(riot_fpath, encoding="utf8") as augments_file:
        game_augments = json.load(augments_file)
        for augment in game_augments["data"]:
            augment_name = game_augments["data"][augment]["name"]
            augment_id = game_augments["data"][augment]["id"]
            temp[augment_id] = augment_name

    with open(custom_fpath, encoding="utf8") as custom_augments_file:
        custom_augments = json.load(custom_augments_file)
        temp.update(custom_augments)

    return temp


items = create_item(os.path.join(SET_INFO_DIR, "tft-item.json"),
                    os.path.join(SET_INFO_DIR, "custom_definitions/item.json"))
traits = create_synergy(os.path.join(SET_INFO_DIR, "tft-trait.json"),
                        os.path.join(SET_INFO_DIR, "custom_definitions/trait.json"))
units = create_champion(os.path.join(SET_INFO_DIR, "tft-champion.json"),
                        os.path.join(SET_INFO_DIR, "custom_definitions/champion.json"))
augments = create_augment(os.path.join(SET_INFO_DIR, "tft-augments.json"),
                          os.path.join(SET_INFO_DIR, "custom_definitions/augments.json"))
