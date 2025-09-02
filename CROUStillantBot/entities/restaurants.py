from asyncpg import Pool, Connection


class Restaurants:
    """
    Classe gérant les restaurants de la base de données.
    """

    def __init__(self, pool: Pool) -> None:
        """
        Initialise les restaurants avec une connexion à la base de données.

        :param pool: La connexion à la base de données.
        :type pool: Pool
        """
        self.pool = pool

    async def getAll(self, actif: bool = True) -> list:
        """
        Récupère tous les restaurants.

        :param actif: Si True, ne récupère que les restaurants actifs, par défaut True
        :type actif: bool, optional
        :return: Les restaurants
        :rtype: list
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            if actif:
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
                            CASE 
                                WHEN IMAGE_URL IS NULL THEN NULL
                                ELSE CONCAT('https://api.croustillant.menu/v1/restaurants/', RID, '/preview')
                            END AS IMAGE_URL,
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
                            ACTIF = TRUE
                    """
                )
            else:
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
                            CASE 
                                WHEN IMAGE_URL IS NULL THEN NULL
                                ELSE CONCAT('https://api.croustillant.menu/v1/restaurants/', RID, '/preview')
                            END AS IMAGE_URL,
                            EMAIL,
                            TELEPHONE,
                            ISPMR,
                            ZONE,
                            PAIEMENT,
                            ACCES,
                            OPENED,
                            ACTIF
                        FROM
                            restaurant
                        JOIN region R ON restaurant.idreg = R.idreg
                        JOIN type_restaurant TPR ON restaurant.idtpr = TPR.idtpr
                    """
                )

    async def getOne(self, id: int) -> dict:
        """
        Récupère un restaurant.

        :param id: ID du restaurant
        :type id: int
        :return: Le restaurant
        :rtype: dict
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
                        CASE 
                            WHEN IMAGE_URL IS NULL THEN NULL
                            ELSE CONCAT('https://api.croustillant.menu/v1/restaurants/', RID, '/preview')
                        END AS IMAGE_URL,
                        EMAIL,
                        TELEPHONE,
                        ISPMR,
                        ZONE,
                        PAIEMENT,
                        ACCES,
                        OPENED,
                        ACTIF
                    FROM
                        restaurant
                    JOIN region R ON restaurant.idreg = R.idreg
                    JOIN type_restaurant TPR ON restaurant.idtpr = TPR.idtpr
                    WHERE
                        rid = $1
                """,
                id,
            )

    async def getInfo(self, id: int) -> dict:
        """
        Récupère un restaurant.

        :param id: ID du restaurant
        :type id: int
        :return: Le restaurant
        :rtype: dict
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
                """,
                id,
            )
