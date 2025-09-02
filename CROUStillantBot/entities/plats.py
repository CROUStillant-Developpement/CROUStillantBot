from asyncpg import Pool, Connection


class Plats:
    """
    Classe gérant les plats de la base de données.
    """

    def __init__(self, pool: Pool) -> None:
        """
        Initialise les plats avec une connexion à la base de données.

        :param pool: La connexion à la base de données.
        :type pool: Pool
        """
        self.pool = pool

    async def getAll(self) -> list:
        """
        Récupère tous les plats.

        :return: Les plats
        :rtype: list
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        *
                    FROM
                        plat
                """
            )

    async def getLast(self, limit: int) -> list:
        """
        Récupère les derniers plats.

        :param limit: Nombre de plats à récupérer
        :type limit: int
        :return: Les plats
        :rtype: list
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        *
                    FROM
                        plat
                    ORDER BY
                        platid DESC
                    LIMIT $1
                """,
                limit,
            )

    async def getOne(self, id: int) -> dict:
        """
        Récupère un plat.

        :param id: ID du plat
        :type id: int
        :return: Le plat
        :rtype: dict
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        *
                    FROM
                        plat
                    WHERE
                        platid = $1
                """,
                id,
            )

    async def getTop(self, limit: int = 100) -> dict:
        """
        Récupère les plat les plus populaires.

        :param limit: Nombre de plats à récupérer
        :type limit: int
        :return: Les plats
        :rtype: dict
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        P.platid,
                        P.libelle,
                        COUNT(C.platid) AS nb
                    FROM
                        plat P
                    JOIN composition C ON P.platid = C.platid
                    JOIN categorie c2 on c2.catid = C.catid
                    JOIN repas R ON c2.rpid = R.rpid
                    JOIN menu M ON R.mid = M.mid
                    JOIN restaurant R2 ON M.rid = R2.rid AND R2.idtpr = 1
                    GROUP BY
                        P.platid
                    ORDER BY
                        nb DESC
                    LIMIT $1;
                """,
                limit,
            )
