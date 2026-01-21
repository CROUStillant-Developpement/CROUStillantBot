from asyncpg import Connection, Pool


class Regions:
    """
    Classe gérant les régions de la base de données.
    """

    def __init__(self, pool: Pool) -> None:
        """
        Initialise les régions avec une connexion à la base de données.

        :param pool: La connexion à la base de données.
        :type pool: Pool
        """
        self.pool = pool

    async def get_all(self) -> list:
        """
        Récupère toutes les régions.

        :return: Les régions
        :rtype: list
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        *
                    FROM
                        region
                """
            )

    async def get_one(self, id: int) -> dict:
        """
        Récupère une région.

        :param id: ID de la région
        :type id: int
        :return: La région
        :rtype: dict
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        *
                    FROM
                        region
                    WHERE
                        idreg = $1
                """,
                id,
            )
