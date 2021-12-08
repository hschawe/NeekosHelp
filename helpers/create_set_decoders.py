import json
import os


def create_set_decoders(rootdir):
    queue_type_decoder = {1090: "Normal", 1100: "Ranked", 1110: "TFT Tutorial", 1130: "Hyper Roll", 1150: "Double Up"}
    region_decoder = {"BR": "br1", "EUNE": "eun1", "EUW": "euw1", "JP": "jp1", "KR": "kr",
                      "LAN": "la1", "LAS": "la2", "NA": "na1", "OCE": "oc1", "TR": "tr1", "RU": "ru"}
    item_decoder = {}
    synergy_decoder = {}
    name_decoder = {}

    # Iterate over all set files
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            # note: since set folders are in order, this will
            # iterate in order of set number
            if file == "champions.json":
                fpath = os.path.join(subdir, file)
                name_decoder = create_champion_decoder(fpath, name_decoder)
            if file == "traits.json":
                fpath = os.path.join(subdir, file)
                synergy_decoder = create_synergy_decoder(fpath, synergy_decoder)
            if file == "items.json":
                fpath = os.path.join(subdir, file)
                item_decoder = create_item_decoder(fpath, item_decoder)

    return queue_type_decoder, name_decoder, synergy_decoder, item_decoder, region_decoder


def create_item_decoder(f, item_decoder):
    with open(f) as items_file:
        items = json.load(items_file)  # List of dictionaries
        for item in items:
            item_decoder[item["id"]] = item["name"]
    return item_decoder


def create_synergy_decoder(f, synergy_decoder):
    with open(f) as synergies_file:
        synergies = json.load(synergies_file)  # List of dictionaries
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


def create_champion_decoder(f, name_decoder):
    with open(f) as names_file:
        names = json.load(names_file)  # List of dictionaries
        for name in names:
            name_decoder[name["championId"]] = name["name"]
    return name_decoder
