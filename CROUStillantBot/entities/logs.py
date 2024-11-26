from asyncpg import Pool, Connection


class Logs:
    MENU_AJOUTE = 1
    MENU_MIS_A_JOUR = 2
    ERREUR_INCONNUE = 3
    IMPOSSIBLE = 4
    PARAMETRES_MODIFIES = 5
    PARAMETRES_SUPPRIMES = 6
    SUPPRESSION_AUTOMATIQUE = 7

    def __init__(self, pool: Pool) -> None:
        self.pool = pool


    async def getLast(self, id: int, limit: int) -> list:
        """
        Récupère les logs d'un serveur

        :return: Les logs du serveur
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
                limit
            )


    async def getFromGuildId(self, id: int) -> dict:
        """
        Récupère les logs d'un serveur

        :return: Les logs du serveur
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
                id
            )


    async def insert(self, id: int, idtpl: int, message: str) -> None:
        """
        Insère les logs d'un serveur

        :return: None
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
