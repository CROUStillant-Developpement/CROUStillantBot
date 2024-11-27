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
            self.client.reload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Impossible de recharger le module `{cog}` : `{e}`")
            
        await ctx.send(f"Module `{cog}` rechargé")


    @commands.command(help="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx: commands.Context, cog: str):
        try:
            self.client.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Impossible de charger le module `{cog}` : `{e}`")
            
        await ctx.send(f"Module `{cog}` chargé")


    @commands.command(help="unload", hidden=True)
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, cog: str):
        try:
            self.client.unload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Impossible de décharger le module `{cog}` : `{e}`")
            
        await ctx.send(f"Module `{cog}` déchargé")
        

    @commands.command(help="logs", hidden=True)
    @commands.is_owner()
    async def logs(self, ctx: commands.Context):
        logs = await self.client.entities.logs.getLast(ctx.guild.id, 50)

        text = ""
        for log in logs:
            text += f"• {getLogEmoji(log.get('idtpl'))} `{log.get('date').strftime('%d/%m/%Y %H:%M:%S')}` • {log.get('message')}\n"

        await ctx.author.send(text)
        await ctx.reply("50 derniers logs ont été envoyés en message privé.")


async def setup(client: commands.Bot):
    await client.add_cog(Development(client))
