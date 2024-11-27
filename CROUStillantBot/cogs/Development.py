from ..utils.functions import getLogEmoji
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


    @commands.command(help="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog: str):
        try:
            await self.client.reload_extension(f"CROUStillantBot.cogs.{cog.title()}")
            await ctx.reply(f"Module `{cog.title()}` rechargé")
        except Exception as e:
            await ctx.reply(f"Impossible de recharger le module `{cog.title()}` : `{e}`")


    @commands.command(help="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx: commands.Context, cog: str):
        try:
            await self.client.load_extension(f"CROUStillantBot.cogs.{cog.title()}")
            await ctx.reply(f"Module `{cog.title()}` chargé")
        except Exception as e:
            await ctx.reply(f"Impossible de charger le module `{cog.title()}` : `{e}`")


    @commands.command(help="unload", hidden=True)
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, cog: str):
        try:
            await self.client.unload_extension(f"CROUStillantBot.cogs.{cog.title()}")
            await ctx.reply(f"Module `{cog.title()}` déchargé")
        except Exception as e:
            await ctx.reply(f"Impossible de décharger le module `{cog.title()}` : `{e}`")
        

    @commands.command(help="logs", hidden=True)
    @commands.is_owner()
    async def logs(self, ctx: commands.Context):
        logs = await self.client.entities.logs.getLast(ctx.guild.id, 50)

        text = ""
        for log in logs:
            text += f"{getLogEmoji(log.get('idtpl'))} `{log.get('log_date').strftime('%d/%m/%Y %H:%M:%S')}` • {log.get('message')}\n"

        if text == "":
            text = "Aucun log n'a été trouvé pour ce serveur."

        await ctx.author.send(text)


async def setup(client: commands.Bot):
    await client.add_cog(Development(client))
