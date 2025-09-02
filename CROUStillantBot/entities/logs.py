from asyncpg import Pool, Connection


class Logs:
    """
    Classe gérant les logs de la base de données.
    """

    MENU_AJOUTE = 1
    MENU_MIS_A_JOUR = 2
    ERREUR_INCONNUE = 3
    IMPOSSIBLE = 4
    PARAMETRES_MODIFIES = 5
    PARAMETRES_SUPPRIMES = 6
    SUPPRESSION_AUTOMATIQUE = 7

    def __init__(self, pool: Pool) -> None:
        """
        Initialise les logs avec une connexion à la base de données.

        :param pool: La connexion à la base de données.
        :type pool: Pool
        """
        self.pool = pool

    async def getLast(self, id: int, limit: int) -> list:
        """
        Récupère les logs d'un serveur

        :param id: ID du serveur
        :type id: int
        :param limit: Nombre de logs à récupérer
        :type limit: int
        :return: Les logs du serveur
        :rtype: list
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT *
                    FROM
                        logs
                    WHERE guild_id = $1
                    ORDER BY log_date DESC
                    LIMIT $2
                """,
                id,
                limit,
            )

    async def getFromGuildId(self, id: int) -> dict:
        """
        Récupère les logs d'un serveur

        :param id: ID du serveur
        :type id: int
        :return: Les logs du serveur
        :rtype: dict
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT *
                    FROM
                        logs
                    WHERE guild_id = $1
                """,
                id,
            )

    async def insert(self, id: int, idtpl: int, message: str) -> None:
        """
        Insère les logs d'un serveur

        :param id: ID du serveur
        :type id: int
        :param idtpl: ID du template de log
        :type idtpl: int
        :param message: Message du log
        :type message: str
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            await connection.execute(
                """
                    INSERT INTO logs (guild_id, idtpl, message)
                    VALUES ($1, $2, $3)
                """,
                id,
                idtpl,
                message,
            )

    async def delete(self, id: int) -> None:
        """
        Supprime les logs d'un serveur

        :param id: ID du serveur
        :type id: int
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            await connection.execute(
                """
                    DELETE FROM logs
                    WHERE guild_id = $1
                """,
                id,
            )
