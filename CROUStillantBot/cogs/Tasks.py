from datetime import datetime

import discord
import pytz

from discord.ext import commands, tasks


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
            "stats.menus",
            "stats.compositions",
            "stats.plats",
            "stats.restaurants",
            "stats.regions",
            f"🕒 • Il est {datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M')}",
            f"📊 • {len(self.client.guilds):,d} serveurs",
        ]

        if messages[self.messageIndex].startswith("stats."):
            stats = await self.client.entities.stats.get()

            stat_type = messages[self.messageIndex].split(".")[1]

            if stat_type == "menus":
                message = f"📋 • Propose {stats['menus']:,d} menus"
            elif stat_type == "compositions":
                message = f"🥗 • {stats['compositions']:,d} compositions"
            elif stat_type == "plats":
                message = f"🍛 • {stats['plats']:,d} plats différents"
            elif stat_type == "restaurants":
                message = f"🍽️ • Scrute {stats['restaurants_actifs']:,d} restaurants"
            elif stat_type == "regions":
                message = f"🌍 • Observe {stats['regions']:,d} régions"
        else:
            message = messages[self.messageIndex]

        await self.client.change_presence(
            activity=discord.CustomActivity(name=message),
            status=discord.Status.online,
        )

        self.messageIndex += 1
        if self.messageIndex >= len(messages):
            self.messageIndex = 0

        if (datetime.now() - self.lastDataRefresh).total_seconds() >= 3600:
            await self.refresh_cache()
            self.lastDataRefresh = datetime.now()

    @task.before_loop
    async def wait_until_ready(self) -> None:
        """
        Attends que le bot soit prêt avant de démarrer la tâche.
        """
        print("[Tasks] CROUStillant n'est pas encore en ligne...")

        # Attends que le bot soit prêt
        await self.client.wait_until_ready()

    async def refresh_cache(self) -> None:
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
