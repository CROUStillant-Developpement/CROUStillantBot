from asyncpg import Pool, Connection


class Restaurants:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool


    async def getAll(self) -> list:
        """
        Récupère tous les restaurants.

        :return: Les restaurants
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        RID,
                        R.IDREG AS IDREG,
                        R.LIBELLE AS REGION,
                        TPR.IDTPR AS IDTPR,
                        TPR.LIBELLE AS TYPE,
                        NOM,
                        ADRESSE,
                        LATITUDE,
                        LONGITUDE,
                        HORAIRES,
                        JOURS_OUVERT,
                        IMAGE_URL,
                        EMAIL,
                        TELEPHONE,
                        ISPMR,
                        ZONE,
                        PAIEMENT,
                        ACCES,
                        OPENED
                    FROM
                        restaurant
                    JOIN region R ON restaurant.idreg = R.idreg
                    JOIN type_restaurant TPR ON restaurant.idtpr = TPR.idtpr
                    WHERE ACTIF = TRUE
                """
            )


    async def getOne(self, id: int) -> dict:
        """
        Récupère un restaurant.

        :param id: ID du restaurant
        :return: Le restaurant
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        RID,
                        R.IDREG AS IDREG,
                        R.LIBELLE AS REGION,
                        TPR.IDTPR AS IDTPR,
                        TPR.LIBELLE AS TYPE,
                        NOM,
                        ADRESSE,
                        LATITUDE,
                        LONGITUDE,
                        HORAIRES,
                        JOURS_OUVERT,
                        IMAGE_URL,
                        EMAIL,
                        TELEPHONE,
                        ISPMR,
                        ZONE,
                        PAIEMENT,
                        ACCES,
                        OPENED
                    FROM
                        restaurant
                    JOIN region R ON restaurant.idreg = R.idreg
                    JOIN type_restaurant TPR ON restaurant.idtpr = TPR.idtpr
                    WHERE
                        rid = $1
                    AND ACTIF = TRUE
                """,
                id
            )


    async def getInfo(self, id: int) -> dict:
        """
        Récupère un restaurant.

        :param id: ID du restaurant
        :return: Le restaurant
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        R.RID,
                        R.AJOUT AS AJOUT,
                        R.MIS_A_JOUR AS MODIFIE,
                        (SELECT COUNT(*) FROM tache_log WHERE rid = $1) AS TACHES
                    FROM
                        restaurant R
                    WHERE
                        R.RID = $1
                    AND ACTIF = TRUE
                """,
                id
            )
