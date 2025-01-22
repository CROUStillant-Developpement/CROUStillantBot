import discord

from .utils.logger import Logger
from .utils.cache import Cache
from .entities.entities import Entities
from discord.ext import commands
from os import listdir, environ
from pathlib import Path
from aiohttp import ClientSession
from dotenv import load_dotenv
from asyncpg import create_pool, Pool


load_dotenv(dotenv_path=".env")


class Bot(commands.Bot):
    """
    Bot
    """
    session: ClientSession
    ready: bool
    maintenance: bool

    def __init__(self):
        intents = discord.Intents(
            messages = True,
            guilds = True
        )
        super().__init__(
            command_prefix = commands.when_mentioned_or("*"), 
            intents=intents, 
            help_command = None,
            owner_ids = [
                852846322478219304, # @polo_byd
            ],
            allowed_mentions = discord.AllowedMentions(
                everyone=False, 
                users=False, 
                roles=False, 
                replied_user=True
            ),
            slash_commands = True,
            activity = discord.CustomActivity(name=f"⚙️ • Chargement en cours..."),
            status = discord.Status.idle
        )


        # Couleur des embeds
        self.color = 0x2F3136
        self.colour = int(environ['COLOUR'], base=16)

        # Chemin du bot
        self.path = str(Path(__file__).parents[0].parents[0])

        # Bannière
        self.banner_url = "https://croustillant.bayfield.dev/banner-small.png"

        # Texte du footer
        self.footer_text = f"CROUStillant • v2.1.0" 


        # Variables
        self.ready = False
        self.maintenance = False


        self.logger = Logger("croustillant")


    async def setup_hook(self) -> None:
        """
        Setup
        """
        for file in listdir(self.path + "/CROUStillantBot/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    await self.load_extension(f"CROUStillantBot.cogs.{file[:-3]}")
                    self.logger.info(f"Loaded {file[:-3]} cog")
                except Exception as e:
                    self.logger.error(f"Error loading {file[:-3]} cog: {e}")


        pool: Pool = await create_pool(
            user=environ["POSTGRES_USER"],
            password=environ["POSTGRES_PASSWORD"],
            database=environ["POSTGRES_DATABASE"],
            host=environ["POSTGRES_HOST"],
            port=environ["POSTGRES_PORT"],
            min_size=10,
            max_size=10
        )
        self.entities = Entities(pool)
        self.cache = Cache(self.entities)

        await self.loadCache()


    async def loadCache(self) -> None:
        """
        Charge le cache
        """
        self.logger.info("Chargement du cache...")

        await self.cache.regions.load()
        await self.cache.restaurants.load()

        self.logger.info("Cache chargé !")
        self.logger.info(f"{len(self.cache.regions)} régions")
        self.logger.info(f"{len(self.cache.restaurants)} restaurants")


    async def on_ready(self) -> None:
        """
        Quand le bot est en ligne
        """
        print("Connecté en tant que")
        print(self.user.name)
        print(self.user.id)

        self.logger.info("Connecté en tant que")
        self.logger.info(self.user.name)
        self.logger.info(self.user.id)
        
        print(f"CROUStillant est désormais en ligne !")
        self.logger.info(f"CROUStillant est désormais en ligne !")
        self.ready = True

        self.avatar_url = self.user.avatar.url


    async def close(self) -> None:
        """
        Ferme le bot
        """
        await self.session.close()
        await super().close()
