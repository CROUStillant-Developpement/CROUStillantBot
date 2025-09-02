from asyncpg import Pool, Connection


class TypesRestaurants:
    """
    Classe gérant les types des restaurants de la base de données.
    """

    def __init__(self, pool: Pool) -> None:
        """
        Initialise les types des restaurants avec une connexion à la base de données.

        :param pool: La connexion à la base de données.
        :type pool: Pool
        """
        self.pool = pool

    async def getAll(self) -> list:
        """
        Récupère tous les types des restaurants.

        :return: Les types des restaurants
        :rtype: list
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT *
                    FROM
                        type_restaurant
                """
            )
