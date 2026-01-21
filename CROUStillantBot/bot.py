from datetime import datetime
from os import environ, listdir
from pathlib import Path

import discord

from aiohttp import ClientSession
from asyncpg import Pool, create_pool
from discord.ext import commands
from dotenv import load_dotenv

from .entities.entities import Entities
from .utils.cache import Cache

load_dotenv(dotenv_path=".env")


class Bot(commands.Bot):
    """
    Bot.
    """

    session: ClientSession
    ready: bool
    maintenance: bool

    def __init__(self) -> None:
        """
        Initialise le bot.
        """
        intents = discord.Intents(messages=True, guilds=True)
        super().__init__(
            command_prefix=commands.when_mentioned_or("*"),
            intents=intents,
            help_command=None,
            owner_ids=[
                852846322478219304,  # @polo_byd
            ],
            allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=True),
            slash_commands=True,
            activity=discord.CustomActivity(name="⚙️ • Chargement en cours..."),
            status=discord.Status.idle,
        )

        # Environnement
        self.env = environ.get("ENV", "dev")

        # Chemin du bot
        self.path = str(Path(__file__).parents[0].parents[0])

        # Bannière
        self.banner_url = "https://croustillant.menu/banner-small.png"

        # Texte du footer
        year = datetime.now().year
        self.footer_text = f"CROUStillant Développement © 2022 - {year} | Tous droits réservés. • `v2.3.0`"

        # Variables
        self.ready = False
        self.maintenance = False

    async def setup_hook(self) -> None:
        """
        Setup.
        """
        for file in listdir(self.path + "/CROUStillantBot/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    await self.load_extension(f"CROUStillantBot.cogs.{file[:-3]}")
                    print(f"Loaded {file[:-3]} cog")
                except Exception as e:
                    print(f"Error loading {file[:-3]} cog: {e}")

        pool: Pool = await create_pool(
            user=environ["POSTGRES_USER"],
            password=environ["POSTGRES_PASSWORD"],
            database=environ["POSTGRES_DATABASE"],
            host=environ["POSTGRES_HOST"],
            port=environ["POSTGRES_PORT"],
            min_size=10,
            max_size=10,
        )
        self.entities = Entities(pool)
        self.cache = Cache(self.entities)

        await self.load_cache()

    async def load_cache(self) -> None:
        """
        Charge le cache.
        """
        print("Chargement du cache...")

        await self.cache.regions.load()
        await self.cache.restaurants.load()

        print("Cache chargé !")
        print(f"{len(self.cache.regions)} régions")
        print(f"{len(self.cache.restaurants)} restaurants")

    async def on_ready(self) -> None:
        """
        Quand le bot est en ligne.
        """
        print("Connecté en tant que")
        print(self.user.name)
        print(self.user.id)

        print("CROUStillant est désormais en ligne !")
        self.ready = True

    async def close(self) -> None:
        """
        Ferme le bot.
        """
        await self.session.close()
        await super().close()
