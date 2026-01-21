from discord.ext import commands

from ..utils.functions import get_log_emoji


class Development(commands.Cog):
    """
    Commandes d'administration du bot.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

    @commands.command(help="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        """
        Synchronise les commandes.

        :param ctx: Le contexte.
        :type ctx: commands.Context
        """
        await self.client.tree.sync()
        await ctx.send("Done")

    @commands.command(help="logout", hidden=True)
    @commands.is_owner()
    async def logout(self, ctx: commands.Context) -> None:
        """
        Déconnecte le bot.

        :param ctx: Le contexte.
        :type ctx: commands.Context
        """
        await ctx.message.add_reaction("✅")

        await ctx.reply("Logging out...")
        await self.client.close()

    @commands.command(help="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog: str) -> None:
        """
        Recharge un module.

        :param ctx: Le contexte.
        :type ctx: commands.Context
        :param cog: Le nom du module.
        :type cog: str
        """
        await ctx.message.add_reaction("✅")

        try:
            await self.client.reload_extension(f"CROUStillantBot.cogs.{cog.title()}")
            await ctx.reply(f"Module `{cog.title()}` rechargé")
        except Exception as e:
            await ctx.reply(f"Impossible de recharger le module `{cog.title()}` : `{e}`")

    @commands.command(help="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx: commands.Context, cog: str) -> None:
        """
        Charge un module.

        :param ctx: Le contexte.
        :type ctx: commands.Context
        :param cog: Le nom du module.
        :type cog: str
        """
        await ctx.message.add_reaction("✅")

        try:
            await self.client.load_extension(f"CROUStillantBot.cogs.{cog.title()}")
            await ctx.reply(f"Module `{cog.title()}` chargé")
        except Exception as e:
            await ctx.reply(f"Impossible de charger le module `{cog.title()}` : `{e}`")

    @commands.command(help="unload", hidden=True)
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, cog: str) -> None:
        """
        Décharge un module.

        :param ctx: Le contexte.
        :type ctx: commands.Context
        :param cog: Le nom du module.
        :type cog: str
        """
        await ctx.message.add_reaction("✅")

        try:
            await self.client.unload_extension(f"CROUStillantBot.cogs.{cog.title()}")
            await ctx.reply(f"Module `{cog.title()}` déchargé")
        except Exception as e:
            await ctx.reply(f"Impossible de décharger le module `{cog.title()}` : `{e}`")

    @commands.command(help="logs", hidden=True)
    @commands.is_owner()
    async def logs(self, ctx: commands.Context) -> None:
        """
        Envoie les logs du serveur en message privé.

        :param ctx: Le contexte.
        :type ctx: commands.Context
        """
        logs = await self.client.entities.logs.get_last(ctx.guild.id, 30)

        text = ""
        for log in logs:
            text += f"{get_log_emoji(log.get('idtpl'))} `{log.get('log_date').strftime('%d/%m/%Y %H:%M:%S')}` • \
{log.get('message')}\n"

        if text == "":
            text = "Aucun log n'a été trouvé pour ce serveur."

        await ctx.message.add_reaction("📩")
        await ctx.author.send(text)

    @commands.command(help="check", hidden=True)
    @commands.is_owner()
    async def check(self, ctx: commands.Context) -> None:
        """
        Vérifie si tous les serveurs ont des logs SERVEUR_AJOUTE (8) pour les serveurs existants.

        :param ctx: Le contexte.
        :type ctx: commands.Context
        """
        await ctx.message.add_reaction("✅")

        async for guild in self.client.fetch_guilds(limit=None):
            logs = await self.client.entities.logs.get_fom_guild_id(guild.id)

            if not any(log.get("idtpl") == self.client.entities.logs.SERVEUR_AJOUTE for log in logs):
                await self.client.entities.logs.insert(
                    guild.id,
                    self.client.entities.logs.SERVEUR_AJOUTE,
                    f"Le bot a été ajouté au serveur {guild.name} ({guild.id})",
                )

                print(f"[Check] Log SERVEUR_AJOUTE ajouté pour le serveur {guild.id}")

        await ctx.reply("Vérification terminée.")


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Development(client))
