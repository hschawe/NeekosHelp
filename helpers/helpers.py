from helpers import create_decoders as decoder

def get_player_traits_from_match(match_data):
    traits_from_api = match_data.get("traits")
    traits = {}
    for trait in traits_from_api:
        traits[trait['name']] = {
            "name": decoder.traits[trait['name']],
            "tier_current": trait['tier_current'],
            "tier_total": trait['tier_total'],
            "num_units": trait['num_units']
        }
    return traits

def get_player_units_from_match(match_data):
    units_from_api = match_data.get("units")
    units = {}
    for unit in units_from_api:
        unit_id = unit['character_id'].lower()
        units[unit_id] = {
            "name": decoder.units.get(unit_id, 'Special Unit'),
            "tier": unit.get('tier', 0),
            "cost": unit.get('rarity', 99),
            "items": unit.get('itemNames', [])
        }
    return units

def get_unit_items(unit):
    items = {}
    for item in unit["items"]:
        items[item] = {
            "name": decoder.items[item]
        }
    return items