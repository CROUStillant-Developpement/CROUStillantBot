import discord

from discord import app_commands
from discord.ext import commands

from ..views.list import ListView


class Mobile(commands.Cog):
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

    # /app

    @app_commands.command(name="app", description="Accèder aux liens de l'application mobile")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def app(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Accèder aux liens de l'application mobile.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        await interaction.response.defer(thinking=True)

        text = (
            "Vous pouvez télécharger [l'application mobile **CROUStillant**](https://mobile.croustillant.menu) via les liens suivants :\n\n"
            "` • ` ~~[**Google Play Store (Android)**](https://mobile.croustillant.menu/android)~~ Prochainement !\n"
            "` • ` [**Apple App Store (iOS)**](https://mobile.croustillant.menu/ios)\n\n"
            "N'hésitez pas à nous faire part de vos retours et suggestions pour améliorer l'application !"
        )
    
        return await interaction.followup.send(
            view=ListView(
                client=self.client,
                content=f"### Application mobile CROUStillant\n\n{text}",
            )
        )


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Mobile(client))
