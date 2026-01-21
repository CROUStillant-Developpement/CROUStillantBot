from asyncpg import Pool

from .logs import Logs
from .menus import Menus
from .parametres import Parametres
from .plats import Plats
from .regions import Regions
from .restaurants import Restaurants
from .stats import Stats
from .types_restaurants import TypesRestaurants


class Entities:
    """
    Classe gérant toutes les entités de la base de données.
    """

    def __init__(self, pool: Pool) -> None:
        """
        Initialise les entités avec une connexion à la base de données.

        :param pool: La connexion à la base de données.
        :type pool: Pool
        """
        self.pool = pool

        self.stats = Stats(pool)
        self.regions = Regions(pool)
        self.restaurants = Restaurants(pool)
        self.types_restaurants = TypesRestaurants(pool)
        self.plats = Plats(pool)
        self.menus = Menus(pool)
        self.parametres = Parametres(pool)
        self.logs = Logs(pool)
