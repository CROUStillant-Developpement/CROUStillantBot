import discord

from ..utils.views import Lien
from discord.ext import commands
from os import environ
from dotenv import load_dotenv


load_dotenv(".env")


class Checks(commands.Cog):
    """
    Gestion des logs.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client
        self.client.tree.interaction_check = self.interaction_check

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Vérifie si une interaction peut être exécutée.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :return: True si l'interaction peut être exécutée, False sinon.
        :rtype: bool
        """
        if interaction.user.bot:
            return False

        if interaction.type == discord.InteractionType.autocomplete:
            if self.client.maintenance or not self.client.ready:
                return False
            else:
                return True
        elif interaction.type == discord.InteractionType.application_command:
            embed = None
            if self.client.maintenance:
                if interaction.user.id in self.client.owner_ids:
                    return True

                embed = discord.Embed(
                    title="Maintenance",
                    description=f"Hey {interaction.user.mention} ! CROUStillant est en maintenance, réessayez plus tard... \n\nExcusez-nous pour la gêne occasionnée.",
                    color=interaction.client.color,
                )
                embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url,
                )
                embed.set_footer(
                    text=interaction.client.footer_text,
                    icon_url=interaction.client.user.display_avatar.url
                )
            elif not self.client.ready:
                embed = discord.Embed(
                    title="Chargement...",
                    description=f"Hey {interaction.user.mention} ! CROUStillant est en train de démarrer, réessayez dans quelques secondes...",
                    color=interaction.client.color,
                )
                embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url,
                )
                embed.set_footer(
                    text=interaction.client.footer_text,
                    icon_url=interaction.client.user.display_avatar.url
                )

            if embed:
                try:
                    await interaction.response.send_message(
                        embed=embed,
                        view=Lien("Aide", environ["DISCORD_INVITE_URL"]),
                        ephemeral=True,
                    )
                except Exception:
                    pass

                return False
            else:
                if interaction.command:
                    print(
                        f"/{interaction.command.qualified_name} - {interaction.user} ({interaction.user.id})"
                    )
                else:
                    print(f"Interaction - {interaction.user} ({interaction.user.id})")

                return True
        else:
            if self.client.maintenance or not self.client.ready:
                return False
            else:
                return True


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Checks(client))
