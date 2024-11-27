from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

 
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.client.logger.info(f"[Events] Serveur quitté : {guild.name} ({guild.id})")

        try:
            await self.client.entities.logs.delete(guild.id)
            await self.client.entities.parametres.delete(guild.id)
        except Exception as e:
            self.client.logger.error(f"[Events] Impossible de supprimer les paramètres du serveur {guild.id} : {e}")
        else:
            self.client.logger.info(f"[Events] Paramètres du serveur {guild.id} supprimés")


async def setup(client):
    await client.add_cog(Events(client))
