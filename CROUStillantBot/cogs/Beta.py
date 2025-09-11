import discord

from ..utils.modal import BetaEmailModal
from discord import app_commands
from discord.ext import commands


class Beta(commands.Cog):
    """
    Beta commandes du bot.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

    # /beta

    @app_commands.command(name="beta", description="S'inscrire au programme beta")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def beta(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        S'inscrire au programme beta.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        await interaction.response.send_modal(BetaEmailModal())


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Beta(client))
