import discord

from discord.ext import commands


class Events(commands.Cog):
    """
    Gestion des événements.
    """

    def __init__(self, client) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """
        Gère le départ du bot d'un serveur.

        :param guild: Le serveur.
        :type guild: discord.Guild
        """
        print(f"[Events] Serveur quitté : {guild.name} ({guild.id})")

        try:
            await self.client.entities.logs.delete(guild.id)
            await self.client.entities.parametres.delete(guild.id)
        except Exception as e:
            print(
                f"[Events] Impossible de supprimer les paramètres du serveur {guild.id} : {e}"
            )
        else:
            print(f"[Events] Paramètres du serveur {guild.id} supprimés")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """
        Gère l'arrivée du bot dans un serveur.

        :param guild: Le serveur.
        :type guild: discord.Guild
        """
        print(f"[Events] Serveur rejoint : {guild.name} ({guild.id})")


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Events(client))
