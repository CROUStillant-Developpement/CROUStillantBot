from time import time

from ..entities.entities import Entities


class CacheObject:
    """
    Objet de cache.
    """

    def __init__(self, entities: Entities, data: list[dict]) -> None:
        """
        Initialise un objet de cache.

        :param entities: Instance de la classe Entities
        :type entities: Entities
        :param data: Données en cache
        :type data: list[dict]
        """
        self.entities = entities
        self.data = data
        self.lastRefresh = None

    async def load(self) -> None:
        """
        Charge les données en cache.
        """
        raise NotImplementedError()

    async def refresh(self) -> None:
        """
        Rafraîchit les données en cache si elles datent de plus de 5 minutes.
        """
        if time() - self.lastRefresh > 300:
            await self.load()

    def __iter__(self) -> "CacheObject":
        """
        Itérateur.

        :return: L'itérateur
        :rtype: CacheObject
        """
        self.index = -1
        return self

    def __next__(self) -> dict:
        """
        Renvoie l'élément suivant.

        :return: L'élément suivant
        :rtype: dict
        :raises StopIteration: Si l'itérateur est arrivé à la fin
        """
        if self.index >= len(self.data) - 1:
            raise StopIteration

        self.index += 1

        return self.data[self.index]

    def __getitem__(self, index: int) -> dict:
        """
        Renvoie l'élément à l'index donné.

        :param index: Index de l'élément
        :type index: int
        :return: L'élément à l'index donné
        :rtype: dict
        :raises IndexError: Si l'index est hors limites
        """
        return self.data[index]

    def __len__(self) -> int:
        """
        Renvoie le nombre d'éléments en cache.

        :return: Nombre d'éléments en cache
        :rtype: int
        """
        return len(self.data)


class Regions(CacheObject):
    """
    Cache des régions.
    """

    def __init__(self, entities: Entities) -> None:
        """
        Initialise le cache des régions.

        :param entities: Instance de la classe Entities
        :type entities: Entities
        """
        super().__init__(entities, [])

    async def load(self) -> None:
        """
        Charge les régions en cache.
        """
        self.data = await self.entities.regions.get_all()
        self.lastRefresh = time()

    async def get_from_id(self, id: int) -> dict | None:
        """
        Renvoie une région à partir de son ID.

        :param id: ID de la région
        :type id: int
        :return: La région ou None si elle n'existe pas
        :rtype: dict | None
        """
        if not self.data:
            raise Exception("Cache pas chargé...")

        return next((region for region in self.data if region.get("idreg") == id), None)

    def __repr__(self) -> str:
        """
        Représentation de l'objet.

        :return: Représentation de l'objet
        :rtype: str
        """
        return f"<Regions regions={self.data}>"


class Restaurants(CacheObject):
    """
    Cache des restaurants.
    """

    def __init__(self, entities: Entities) -> None:
        """
        Initialise le cache des restaurants.

        :param entities: Instance de la classe Entities
        :type entities: Entities
        """
        super().__init__(entities, [])

    async def load(self) -> None:
        """
        Charge les restaurants en cache.
        """
        self.data = await self.entities.restaurants.get_all()
        self.lastRefresh = time()

    async def get_from_id(self, id: int) -> dict | None:
        """
        Renvoie un restaurant à partir de son ID.

        :param id: ID du restaurant
        :type id: int
        :return: Le restaurant ou None si il n'existe pas
        :rtype: dict | None
        """
        if not self.data:
            raise Exception("Cache pas chargé...")

        return next(
            (restaurant for restaurant in self.data if restaurant.get("rid") == id),
            None,
        )

    async def get_from_region_id(self, id: int) -> list[dict]:
        """
        Renvoie les restaurants d'une région à partir de l'ID de la région.

        :param id: ID de la région
        :type id: int
        :return: Liste des restaurants de la région
        :rtype: list[dict]
        """
        if not self.data:
            raise Exception("Cache pas chargé...")

        return [restaurant for restaurant in self.data if restaurant.get("idreg") == id]

    def __repr__(self) -> str:
        """
        Représentation de l'objet.

        :return: Représentation de l'objet
        :rtype: str
        """
        return f"<Restaurants regions={len(self.data)}>"


class Cache:
    """
    Cache.
    """

    def __init__(self, entities: Entities) -> None:
        """
        Initialise le cache.

        :param entities: Instance de la classe Entities
        :type entities: Entities
        """
        self.regions = Regions(entities)
        self.restaurants = Restaurants(entities)
