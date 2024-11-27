from ..entities.entities import Entities
from time import time


class CacheObject:
    def __init__(self, entities: Entities, data: list[dict]) -> None:
        self.entities = entities
        self.data = data
        self.lastRefresh = None


    async def load(self) -> None:
        raise NotImplementedError()


    async def refresh(self) -> None:
        if time() - self.lastRefresh > 300:
            await self.load()


    def __iter__(self):
        self.index = -1
        return self


    def __next__(self):
        if self.index >= len(self.data) - 1:
            raise StopIteration

        self.index += 1

        return self.data[self.index]


    def __getitem__(self, index: int) -> dict:
        return self.data[index]


    def __len__(self) -> int:
        return len(self.data)


class Regions(CacheObject):
    def __init__(self, entities: Entities) -> None:
        super().__init__(entities, [])
        

    async def load(self) -> None:
        self.data = await self.entities.regions.getAll()
        self.lastRefresh = time()


    async def getFromId(self, id: int) -> dict|None:
        if not self.data:
            raise Exception(f"Cache pas chargé...")
    
        return next((region for region in self.data if region.get("idreg") == id), None)


    def __repr__(self) -> str:
        return f"<Regions regions={self.data}>"


class Restaurants(CacheObject):
    def __init__(self, entities: Entities) -> None:
        super().__init__(entities, [])


    async def load(self) -> None:
        self.data = await self.entities.restaurants.getAll()
        self.lastRefresh = time()


    async def getFromId(self, id: int) -> dict|None:
        if not self.data:
            raise Exception(f"Cache pas chargé...")

        return next((restaurant for restaurant in self.data if restaurant.get("rid") == id), None)


    async def getFromRegionID(self, id: int) -> list[dict]:
        if not self.data:
            raise Exception(f"Cache pas chargé...")
        
        return [
            restaurant for restaurant in self.data if restaurant.get("idreg") == id
        ]


    def __repr__(self) -> str:
        return f"<Restaurants regions={len(self.data)}>"


class Cache:
    """
    Cache
    """
    def __init__(self, entities: Entities) -> None:
        """
        Initialise le cache
        """
        self.regions = Regions(entities)
        self.restaurants = Restaurants(entities)
