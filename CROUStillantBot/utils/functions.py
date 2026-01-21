from datetime import datetime, timedelta

import discord
import pytz

from .constants import CLOCKS
from .date import get_clean_date


def get_clock_emoji(dt: datetime) -> str:
    """
    Récupère l'emoji de l'heure.

    :param dt: Une date
    :type dt: datetime
    :return: Unicode de l'emoji
    :rtype: str
    """
    round_to = 30 * 60
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    time = dt + timedelta(0, rounding - seconds, -dt.microsecond)
    return CLOCKS[time.strftime("%I:%M")]


def get_log_emoji(idtpl: int) -> str:
    """
    Récupère l'emoji du log.

    :param idtpl: ID du template
    :type idtpl: int
    :return: Unicode de l'emoji
    :rtype: str
    """
    emojis = {
        1: "📩",  # Menu ajouté
        2: "🔄",  # Menu mis à jour
        3: "❌",  # Erreur lors de la mise à jour du menu
        4: "🚫",  # Impossible de modifier le menu
        5: "🔧",  # Paramètres modifiés
        6: "🗑️",  # Paramètres modifiés
        7: "🔥",  # Suppression automatique des paramètres
        8: "🆕",  # Serveur ajouté
        9: "📋",  # Serveur supprimé
    }
    return emojis.get(idtpl, "❓")


def create_option(restaurant: dict, menu: dict, default: bool = False) -> discord.SelectOption:
    """
    Créer une option.

    :param restaurant: Restaurant
    :type restaurant: dict
    :param menu: Menu
    :type menu: dict
    :param default: Default
    :type default: bool
    :return: discord.SelectOption
    :rtype: discord.SelectOption
    """
    if menu is None:
        date = datetime.now(tz=pytz.timezone("Europe/Paris"))
    else:
        date = datetime.strptime(menu.get("date").strftime("%d-%m-%Y"), "%d-%m-%Y")

    return discord.SelectOption(
        label=get_clean_date(date),
        description=f"{restaurant.get('zone')} • {restaurant.get('nom')}",
        value=date.strftime("%d-%m-%Y"),
        emoji="🍽️",
        default=default,
    )


def get_crous_link(restaurant: dict) -> str:
    """
    Récupère le lien du CROUS.

    :param restaurant: Restaurant
    :type restaurant: dict
    :return: Titre et lien
    :rtype: tuple[str, str]
    """
    return (
        "Site officiel de CROUStillant",
        f"https://croustillant.menu/fr/restaurants/{restaurant.get('rid')}",
    )
