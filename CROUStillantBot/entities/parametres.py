from asyncpg import Pool, Connection


class Parametres:
    """
    Classe gérant les paramètres de la base de données.
    """

    def __init__(self, pool: Pool) -> None:
        """
        Initialise les paramètres avec une connexion à la base de données.

        :param pool: La connexion à la base de données.
        :type pool: Pool
        """
        self.pool = pool

    async def count(self, id: int) -> int:
        """
        Compte le nombre de paramètres d'un serveur

        :param id: ID du serveur
        :type id: int
        :return: Le nombre de paramètres du serveur
        :rtype: int
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchval(
                """
                    SELECT COUNT(*)
                    FROM
                        parametres
                    WHERE guild_id = $1
                """,
                id,
            )

    async def getAll(self) -> list:
        """
        Récupère les paramètres de tous les serveurs

        :return: Les paramètres de tous les serveurs
        :rtype: list
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT *
                    FROM
                        parametres
                """
            )

    async def getFromGuildId(self, id: int) -> dict:
        """
        Récupère les paramètres d'un serveur

        :param id: ID du serveur
        :type id: int
        :return: Les paramètres du serveur
        :rtype: dict
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT *
                    FROM
                        parametres
                    WHERE guild_id = $1
                """,
                id,
            )

    async def checkIfExist(self, id: int, rid: int) -> dict:
        """
        Vérifie si les paramètres d'un serveur existent

        :param id: ID du serveur
        :type id: int
        :param rid: ID du restaurant
        :type rid: int
        :return: Retourne les paramètres du serveur
        :rtype: dict
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT *
                    FROM
                        parametres
                    WHERE guild_id = $1 AND rid = $2
                """,
                id,
                rid,
            )

    async def update(
        self, id: int, channel_id: id, message_id: int, rid: int, theme: str, repas: str
    ) -> None:
        """
        Met à jour les paramètres d'un serveur

        :param id: ID du serveur
        :type id: int
        :param channel_id: ID du channel
        :type channel_id: int
        :param message_id: ID du message
        :type message_id: int
        :param rid: ID du restaurant
        :type rid: int
        :param theme: Thème du menu
        :type theme: str
        :param repas: Type de repas
        :type repas: str
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            await connection.execute(
                """
                    UPDATE parametres
                    SET
                        channel_id = $2,
                        message_id = $3,
                        theme = $5,
                        repas = $6
                    WHERE guild_id = $1 AND rid = $4
                """,
                id,
                channel_id,
                message_id,
                rid,
                theme,
                repas,
            )

    async def insert(
        self, id: int, channel_id: id, message_id: int, rid: int, theme: str, repas: str
    ) -> None:
        """
        Insère les paramètres d'un serveur

        :param id: ID du serveur
        :type id: int
        :param channel_id: ID du channel
        :type channel_id: int
        :param message_id: ID du message
        :type message_id: int
        :param rid: ID du restaurant
        :type rid: int
        :param theme: Thème du menu
        :type theme: str
        :param repas: Type de repas
        :type repas: str
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            await connection.execute(
                """
                    INSERT INTO parametres (guild_id, channel_id, message_id, rid, theme, repas)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """,
                id,
                channel_id,
                message_id,
                rid,
                theme,
                repas,
            )

    async def delete(self, id: int, rid: int = None) -> None:
        """
        Supprime les paramètres d'un serveur

        :param id: ID du serveur
        :type id: int
        :param rid: ID du restaurant
        :type rid: int
        """
        if rid is None:
            async with self.pool.acquire() as connection:
                connection: Connection

                await connection.execute(
                    """
                        DELETE FROM parametres
                        WHERE guild_id = $1
                    """,
                    id,
                )
        else:
            async with self.pool.acquire() as connection:
                connection: Connection

                await connection.execute(
                    """
                        DELETE FROM parametres
                        WHERE guild_id = $1 AND rid = $2
                    """,
                    id,
                    rid,
                )
