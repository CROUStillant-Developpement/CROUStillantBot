from datetime import datetime


def getCleanDate(date: datetime) -> str:
    """
    Renvoie une date formatée.

    :param date: Date à formater.
    :type date: datetime

    :return: Date formatée.
    :rtype: str
    """
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    return f"{jours[int(date.strftime('%w'))-1].title()} {date.day} {mois[int(date.strftime('%m'))-1]} {date.year}"


def getDateFromInput(date: str) -> datetime:
    """
    Converti un input en datetime.
    
    :param date: Date à convertir.
    :type date: str
    
    :return: Date convertie.
    :rtype: datetime
    
    :raises ValueError: Si la date n'est pas au bon format.
    
    :example:
    >>> getDateFromInput("12-12-2021")
    datetime.datetime(2021, 12, 12, 0, 0)
    
    >>> getDateFromInput("12-12-21")
    datetime.datetime(2021, 12, 12, 0, 0)
    
    >>> getDateFromInput("12 12 2021")
    datetime.datetime(2021, 12, 12, 0, 0)
    
    >>> getDateFromInput("12 12 21")
    datetime.datetime(2021, 12, 12, 0, 0)
    """
    try:
        date = datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        if "-" in date:
            format1 = "%d-%m-%y"
            format2 = "%d-%m-%Y"
        elif " " in date:
            format1 = "%d %m %y"
            format2 = "%d %m %Y"
        elif "/" in date:
            format1 = "%d/%m/%y"
            format2 = "%d/%m/%Y"

        try:
            date: datetime = datetime.strptime(date, format1)
        except ValueError:
            try:
                date: datetime = datetime.strptime(date, format2)
            except ValueError:
                raise ValueError

    return date
