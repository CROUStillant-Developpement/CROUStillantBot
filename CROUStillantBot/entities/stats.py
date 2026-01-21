from asyncpg import Connection, Pool


class Stats:
    """
    Classe gérant les statistiques de la base de données.
    """

    def __init__(self, pool: Pool) -> None:
        """
        Initialise les statistiques avec une connexion à la base de données.

        :param pool: La connexion à la base de données.
        :type pool: Pool
        """
        self.pool = pool

    async def get(self) -> list:
        """
        Récupère toutes les statistiques.

        :return: Les statistiques.
        :rtype: dict
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT * FROM v_stats;
                """
            )
