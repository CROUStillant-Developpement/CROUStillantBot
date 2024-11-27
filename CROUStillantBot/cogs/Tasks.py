import discord
import pytz

from discord.ext import commands, tasks
from datetime import datetime


class Tasks(commands.Cog):
    """
    Tâches de fond du bot.
    """
    def __init__(self, client: commands.Bot):
        self.client = client

        self.task.start()

        self.messageIndex = 0
        
        self.lastDataRefresh = datetime.now()


    def cog_unload(self):
        self.task.cancel()


    def cog_reload(self):
        self.task.cancel()


    @tasks.loop(seconds=15)
    async def task(self):
        messages = [
            f"🌍 • Observe {len(self.client.cache.regions):,d} régions",
            f"🍽️ • Scrute {len(self.client.cache.restaurants):,d} restaurants",
            f"🕒 • Il est {datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M')}",
            f"📊 • {len(self.client.guilds):,d} serveurs",
        ]

        await self.client.change_presence(
            activity=discord.CustomActivity(name=messages[self.messageIndex]),
            status=discord.Status.online
        )

        self.messageIndex += 1
        if self.messageIndex >= len(messages):
            self.messageIndex = 0


        if (datetime.now() - self.lastDataRefresh).total_seconds() >= 3600:
            await self.refreshCache()
            self.lastDataRefresh = datetime.now()


    @task.before_loop
    async def wait_until_ready(self):
        self.client.logger.info("[Tasks] CROUStillant n'est pas encore en ligne...")
        
        # Attends que le bot soit prêt
        await self.client.wait_until_ready()


    async def refreshCache(self) -> None:
        """
        Rafraîchit les données en cache.
        """
        await self.client.cache.regions.refresh()
        await self.client.cache.restaurants.refresh()


async def setup(client: commands.Bot):
    await client.add_cog(Tasks(client))
