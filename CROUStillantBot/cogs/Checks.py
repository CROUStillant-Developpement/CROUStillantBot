import discord

from ..views.error import ErrorView
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
            if interaction.command:
                print(
                    f"/{interaction.command.qualified_name} - {interaction.user} ({interaction.user.id})"
                )
            else:
                print(f"Interaction - {interaction.user} ({interaction.user.id})")

            if self.client.maintenance:
                if interaction.user.id in self.client.owner_ids:
                    return True

                await interaction.response.send_message(
                    ephemeral=True,
                    view=ErrorView(
                        client=self.client,
                        content="## Maintenance\n\nCROUStillant est actuellement en maintenance, réessayez plus tard...\n\nExcusez-nous pour la gêne occasionnée.",
                        lien=environ["DISCORD_INVITE_URL"],
                    ),
                )
                return False
            elif not self.client.ready:
                await interaction.response.send_message(
                    ephemeral=True,
                    view=ErrorView(
                        client=self.client,
                        content="## Chargement...\n\nCROUStillant est en train de démarrer, réessayez dans quelques secondes...",
                        lien=environ["DISCORD_INVITE_URL"],
                    ),
                )
                return False
            else:
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
