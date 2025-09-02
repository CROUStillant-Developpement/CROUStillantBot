import discord
import pytz

from discord.ext import commands, tasks
from datetime import datetime


class Tasks(commands.Cog):
    """
    Tâches de fond du bot.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

        self.task.start()

        self.messageIndex = 0

        self.lastDataRefresh = datetime.now()

    def cog_unload(self) -> None:
        """
        Arrête la tâche lorsque le module est déchargé.
        """
        self.task.cancel()

    def cog_reload(self) -> None:
        """
        Arrête la tâche lorsque le module est rechargé.
        """
        self.task.cancel()

    @tasks.loop(seconds=15)
    async def task(self) -> None:
        """
        Change le statut du bot et rafraîchit les données en cache toutes les heures.
        """
        messages = [
            f"🌍 • Observe {len(self.client.cache.regions):,d} régions",
            f"🍽️ • Scrute {len(self.client.cache.restaurants):,d} restaurants",
            f"🕒 • Il est {datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M')}",
            f"📊 • {len(self.client.guilds):,d} serveurs",
        ]

        await self.client.change_presence(
            activity=discord.CustomActivity(name=messages[self.messageIndex]),
            status=discord.Status.online,
        )

        self.messageIndex += 1
        if self.messageIndex >= len(messages):
            self.messageIndex = 0

        if (datetime.now() - self.lastDataRefresh).total_seconds() >= 3600:
            await self.refreshCache()
            self.lastDataRefresh = datetime.now()

    @task.before_loop
    async def wait_until_ready(self) -> None:
        """
        Attends que le bot soit prêt avant de démarrer la tâche.
        """
        print("[Tasks] CROUStillant n'est pas encore en ligne...")

        # Attends que le bot soit prêt
        await self.client.wait_until_ready()

    async def refreshCache(self) -> None:
        """
        Rafraîchit les données en cache.
        """
        await self.client.cache.regions.refresh()
        await self.client.cache.restaurants.refresh()


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Tasks(client))
