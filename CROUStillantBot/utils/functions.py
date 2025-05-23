import unicodedata
import discord
import pytz

from .date import getCleanDate
from .constants import CLOCKS
from datetime import datetime, timedelta


def getClockEmoji(dt: datetime) -> str:
    """
    Récupère l'emoji de l'heure
    
    :param dt: datetime
    :return: str
    """
    roundTo=30*60
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    time = dt + timedelta(0,rounding-seconds,-dt.microsecond)
    return CLOCKS[time.strftime("%I:%M")]


def getLogEmoji(idtpl: int) -> str:
    """
    Récupère l'emoji du log
    
    :param idtpl: ID du template
    :type idtpl: int
    :return: str
    """
    emojis = {
        1: "📝",
        2: "🔄",
        3: "❌",
        4: "🚫",
        5: "🔧",
        6: "🗑️",
        7: "🔥"
    }
    return emojis.get(idtpl, "❓")


def createOption(restaurant: dict, menu: dict, default: bool = False) -> discord.SelectOption:
    """
    Créer une option
    
    :param restaurant: Restaurant
    :type restaurant: dict
    :param menu: Menu
    :type menu: dict
    :param default: Default
    :type default: bool
    :return: discord.SelectOption
    """
    if menu is None:
        date = datetime.now(tz=pytz.timezone("Europe/Paris"))
    else:
        date = datetime.strptime(menu.get("date").strftime("%d-%m-%Y"), "%d-%m-%Y")

    return discord.SelectOption(
        label=getCleanDate(date),
        description=f"{restaurant.get('zone')} • {restaurant.get('nom')}",
        value=date.strftime("%d-%m-%Y"),
        emoji="🍽️",
        default=default
    )


def getCrousLink(region: dict, restaurant: dict) -> str:
    """
    Récupère le lien du CROUS
    
    :param region: Region
    :type region: dict
    :param restaurant: Restaurant
    :type restaurant: dict
    :return: str
    """
    # region_str = region.get("libelle").lower().replace(".", "-")
    # if region_str == "nancy-metz":
    #     region_str = "lorraine"

    # ru_str = unicodedata.normalize('NFKD', restaurant.get("nom").lower()).encode("ascii", "ignore").decode("utf-8").replace(" ", "-").replace("'", "")

    # return f"www.crous-{region_str}.fr", f"https://www.crous-{region_str}.fr/restaurant/{ru_str}"
    return "Site officiel de CROUStillant", f"https://croustillant.menu/fr/restaurants/{restaurant.get("rid")}"
