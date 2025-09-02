import pytz

from datetime import datetime


class Error(Exception):
    """
    Classe de base pour les erreurs personnalisées.
    """

    def __init__(
        self, error: str = "Une erreur est survenue lors de la requête."
    ) -> None:
        """
        Initialise une erreur personnalisée.

        :param error: Message d'erreur
        :type error: str
        """
        self.error = error
        super().__init__(self.error)


class RegionIntrouvable(Error):
    """
    Initialise une erreur de région introuvable.
    """

    def __init__(self) -> None:
        """
        Initialise une erreur de région introuvable.
        """
        self.error = "Cette région est introuvable !"
        self.code = 404
        super().__init__(self.error)


class RestaurantIntrouvable(Error):
    """
    Initialise une erreur de restaurant introuvable.
    """

    def __init__(self) -> None:
        """
        Initialise une erreur de restaurant introuvable.
        """
        self.error = "Ce restaurant est introuvable !"
        self.code = 404
        super().__init__(self.error)


class MenuIntrouvable(Error):
    """
    Initialise une erreur de menu introuvable.
    """

    def __init__(self) -> None:
        """
        Initialise une erreur de menu introuvable.
        """
        self.error = "Le menu n'est pas disponible !"
        self.code = 404
        self.date = datetime.now(tz=pytz.timezone("Europe/Paris"))
        super().__init__(self.error)
