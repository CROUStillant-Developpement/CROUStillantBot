import discord
from discord import app_commands
from discord.ext import commands


class Development(commands.Cog):
    """
    Commandes d'administration du bot.
    """
    def __init__(self, client: commands.Bot):
        self.client = client


    @commands.command(help="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        await self.client.tree.sync()
        await ctx.send("Done")


    @commands.command(help="logout", hidden=True)
    @commands.is_owner()
    async def logout(self, ctx: commands.Context):
        await ctx.send("Logging out...")
        await self.client.close()


async def setup(client: commands.Bot):
    await client.add_cog(Development(client))
