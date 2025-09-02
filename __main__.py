import asyncio

from CROUStillantBot.bot import Bot
from os import environ
from dotenv import load_dotenv
from aiohttp import ClientSession


load_dotenv(dotenv_path=".env")


async def main():
    """
    Lance le bot
    """
    client = Bot()

    async with ClientSession() as session:
        async with client:
            client.session = session
            await client.start(environ["TOKEN"], reconnect=True)


asyncio.run(main())
