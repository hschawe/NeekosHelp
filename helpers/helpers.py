import logging
import discord
from helpers import create_decoders as decoder


logger = logging.getLogger(__name__)


def get_player_traits_from_match(match_data):
    """Function that transforms player match riot api data."""
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
    """Function that transforms player units riot api data."""
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


def get_player_augments_from_match(match_data):
    """Function that transforms player augments riot api data."""
    augments_from_api = match_data.get("augments")
    augment_names = []
    for augment_id in augments_from_api:
        try:
            augment_name = decoder.augments.get(augment_id)
            augment_names.append(augment_name)
        except KeyError:
            augment_names.append(augment_id)
            print(f"Augment ID not in augment decoder: {augment_id}")
    return augment_names


def get_unit_items(unit):
    """Function that serializes item data that a unit has."""
    items = {}
    for item in unit["items"]:
        items[item] = {
            "name": decoder.items[item]
        }
    return items


async def sync_to_guild(bot, guild_id):
    """Syncs commands only to one guild for testing slash commands"""
    test_guild = discord.Object(id=guild_id)

    bot.tree.copy_global_to(guild=test_guild)
    cmds = await bot.tree.sync(guild=test_guild)
    cmds_strs = str([cmd.name for cmd in cmds])
    logger.info(f"Slash commands have been synchronized to the test discord (guild ID = {guild_id}).")
    logger.info(f"Synced commands: {cmds_strs}.")
    return
