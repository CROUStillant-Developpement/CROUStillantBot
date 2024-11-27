import pytz

from datetime import datetime


class Error(Exception):
    def __init__(self, error: str = "Une erreur est survenue lors de la requête."):
        self.error = error
        super().__init__(self.error)


class RegionIntrouvable(Error):
    def __init__(self):
        self.error = "Cette région est introuvable !"
        self.code = 404
        super().__init__(self.error)


class RestaurantIntrouvable(Error):
    def __init__(self):
        self.error = "Ce restaurant est introuvable !"
        self.code = 404
        super().__init__(self.error)


class MenuIntrouvable(Error):
    def __init__(self):
        self.error = "Le menu n'est pas disponible !"
        self.code = 404
        self.date = datetime.now(tz=pytz.timezone("Europe/Paris"))
        super().__init__(self.error)
