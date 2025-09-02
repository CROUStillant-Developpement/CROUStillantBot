from .stats import Stats
from .regions import Regions
from .restaurants import Restaurants
from .types_restaurants import TypesRestaurants
from .plats import Plats
from .menus import Menus
from .parametres import Parametres
from .logs import Logs
from asyncpg import Pool


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
