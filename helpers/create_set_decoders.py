import json
import os


def create_set_decoders(rootdir):
    queue_type_decoder = {1090: "Normal", 1100: "Ranked", 1110: "TFT Tutorial", 1130: "Hyper Roll", 1150: "Double Up"}
    game_types = {"pairs": "Double Up", "standard": "Ranked", "normal": "Normal", "turbo": "Hyper Roll"}
    region_decoder = {"BR": "br1", "EUNE": "eun1", "EUW": "euw1", "JP": "jp1", "KR": "kr",
                      "LAN": "la1", "LAS": "la2", "NA": "na1", "OCE": "oc1", "TR": "tr1", "RU": "ru"}
    rarity_decoder = {0: '1 cost', 1:'2 cost', 2:'3 cost',4:'4 cost',6:'5 cost'}
    item_decoder = {}
    synergy_decoder = {}
    name_decoder = {}

    # Iterate over all set files
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            # note: since set folders are in order, this will
            # iterate in order of set number
            if file == "tft-champion.json":
                fpath = os.path.join(subdir, file)
                name_decoder = create_champion_decoder(fpath, name_decoder)
            if file == "tft-trait.json":
                fpath = os.path.join(subdir, file)
                synergy_decoder = create_synergy_decoder(fpath, synergy_decoder)
            if file == "tft-item.json":
                fpath = os.path.join(subdir, file)
                item_decoder = create_item_decoder(fpath, item_decoder)

    return queue_type_decoder, game_types, name_decoder, synergy_decoder, item_decoder, region_decoder, rarity_decoder


def create_item_decoder(f, item_decoder):
    with open(f) as items_file:
        items = json.load(items_file)  # List of dictionaries
        for key, item in items["data"].items():
            item_decoder[item["id"]] = item["name"]
    return item_decoder


def create_synergy_decoder(f, synergy_decoder):
    with open(f) as synergies_file:
        synergies = json.load(synergies_file)  # List of dictionaries
        for synergy in synergies['data']:
            synergy_key = synergy
            synergy_name = synergies['data'][synergy_key]['name']
            synergy_decoder[synergy_key] = synergy_name
    return synergy_decoder


def create_champion_decoder(f, name_decoder):
    with open(f) as names_file:
        names = json.load(names_file)  # List of dictionaries
        for name in names['data']:
            champ_name = names['data'][name]["name"]
            id = names['data'][name]["id"].lower()
            name_decoder[id] = champ_name
    return name_decoder
