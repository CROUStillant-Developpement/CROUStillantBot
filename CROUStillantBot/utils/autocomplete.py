import discord

from discord import app_commands


async def region_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    """
    Autocomplete pour les régions.

    :param interaction: Interaction
    :type interaction: discord.Interaction
    :param current: Texte actuel
    :type current: str
    :return: List[app_commands.Choice]
    :rtype: list
    """
    return [
        app_commands.Choice(name=region.get("libelle"), value=region.get("idreg"))
        for region in interaction.client.cache.regions
        if current.lower() in region.get("libelle").lower() or current.lower() in str(region.get("idreg"))
    ][:25]


async def restaurant_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    """
    Autocomplete pour les restaurants.

    :param interaction: Interaction
    :type interaction: discord.Interaction
    :param current: Texte actuel
    :type current: str
    :return: List[app_commands.Choice]
    :rtype: list
    """
    return [
        app_commands.Choice(name=f"{restaurant.get('nom')}", value=restaurant.get("rid"))
        for restaurant in interaction.client.cache.restaurants
        if current.lower() in restaurant.get("nom").lower() or current.lower() in str(restaurant.get("rid"))
    ][:25]
