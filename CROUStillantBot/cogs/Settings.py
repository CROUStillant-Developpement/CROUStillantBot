import discord

from ..utils.autocomplete import restaurant_autocomplete
from ..utils.functions import getLogEmoji
from discord import app_commands
from discord.ext import commands
from typing import Literal
from datetime import datetime


class Settings(commands.Cog):
    """
    Paramètres du bot pour les serveurs.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

    config = app_commands.Group(
        name="config", description="Commandes de configuration du bot", guild_only=True
    )

    # /config menu

    @config.command(name="menu", description="Configuration du menu automatique")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(channel="Un salon")
    @app_commands.describe(restaurant="Un restaurant")
    @app_commands.describe(repas="Un repas (matin, midi, soir) - par défaut : midi")
    @app_commands.describe(
        theme="Un thème (clair, sombre, violet) - par défaut : clair"
    )
    @app_commands.autocomplete(restaurant=restaurant_autocomplete)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def menu(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        restaurant: int,
        repas: Literal["matin", "midi", "soir"] = "midi",
        theme: Literal["clair", "sombre"] = "clair",
    ) -> None:
        """
        Configure le menu automatique.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param channel: Le salon où envoyer le menu.
        :type channel: discord.TextChannel
        :param restaurant: Le restaurant.
        :type restaurant: int
        :param repas: Le repas (matin, midi, soir).
        :type repas: Literal["matin", "midi", "soir"]
        :param theme: Le thème (clair, sombre, violet).
        :type theme: Literal["clair", "sombre", "violet"]
        """
        await interaction.response.defer(thinking=True)

        if theme == "clair":
            theme = "light"
        elif theme == "sombre":
            theme = "dark"
        elif theme == "violet":
            theme = "purple"

        settings = await self.client.entities.parametres.checkIfExist(
            interaction.guild_id, restaurant
        )
        if not settings:
            count = await self.client.entities.parametres.count(interaction.guild_id)

            if count >= 2:
                embed = discord.Embed(
                    title="Limite de configurations atteinte",
                    description="Vous avez atteint la limite de configurations pour les menus automatiques.\n\nSupprimez une configuration pour en ajouter une nouvelle.",
                    color=self.client.colour,
                )
                embed.set_image(url=self.client.banner_url)
                embed.set_footer(
                    text=self.client.footer_text, icon_url=self.client.user.display_avatar.url
                )
                return await interaction.followup.send(embed=embed)

            await self.client.entities.parametres.insert(
                interaction.guild_id, channel.id, None, restaurant, theme, repas
            )
            await self.client.entities.logs.insert(
                interaction.guild_id,
                self.client.entities.logs.PARAMETRES_MODIFIES,
                f"Configuration du menu automatique pour le restaurant ` {restaurant} ` dans le salon ` #{channel.name} ` pour le repas du ` {repas} ` avec le thème ` {theme} `.",
            )
        else:
            await self.client.entities.parametres.update(
                interaction.guild_id,
                channel.id,
                settings.get("message_id")
                if settings.get("channel_id") == channel.id
                else None,
                restaurant,
                theme,
                repas,
            )
            await self.client.entities.logs.insert(
                interaction.guild_id,
                self.client.entities.logs.PARAMETRES_MODIFIES,
                f"Mise à jour du menu automatique pour le restaurant ` {restaurant} ` dans le salon ` #{channel.name} ` pour le repas du {repas} avec le thème ` {theme} `.",
            )

        now = datetime.now()
        if now.hour == 23:
            next_hour = datetime(now.year, now.month, now.day + 1, 0)
        else:
            next_hour = datetime(now.year, now.month, now.day, now.hour + 1, 0)
        diff = next_hour - now
        timestamp = int((now.timestamp() + diff.total_seconds()))

        embed = discord.Embed(
            title="Menu automatique configuré",
            description=f"Le menu automatique a été configuré pour le restaurant ` {restaurant} ` dans le salon ` #{channel.name} ` ({channel.mention}) pour le repas du ` {repas} ` avec le thème ` {theme} `.\n\n**Le menu sera envoyé <t:{timestamp}:R> (<t:{timestamp}>).**",
            color=self.client.colour,
        )
        embed.set_image(url=self.client.banner_url)
        embed.set_footer(text=self.client.footer_text, icon_url=self.client.user.display_avatar.url)

        embed2 = discord.Embed(
            title="Informations",
            description="Le menu sera mis à jour toutes les heures.",
            color=self.client.colour,
        )
        embed2.set_image(url=self.client.banner_url)
        embed2.set_footer(text=self.client.footer_text, icon_url=self.client.user.display_avatar.url)

        return await interaction.followup.send(embeds=[embed, embed2])

    # /config logs
    @config.command(name="logs", description="Voir les logs du serveur")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def logs(self, interaction: discord.Interaction) -> None:
        """
        Envoie les logs du serveur.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        await interaction.response.defer(thinking=True)

        logs = await self.client.entities.logs.getLast(interaction.guild.id, 20)
        if not logs:
            embed = discord.Embed(
                title="Logs introuvables",
                description="Aucun log n'a été trouvé pour ce serveur.",
                color=self.client.colour,
            )
            embed.set_image(url=self.client.banner_url)
            embed.set_footer(
                text=self.client.footer_text, icon_url=self.client.user.display_avatar.url
            )
            return await interaction.followup.send(embed=embed)

        embed = discord.Embed(
            title="20 derniers logs",
            description="\n".join(
                [
                    f"{getLogEmoji(log.get('idtpl'))} `{log.get('log_date').strftime('%d/%m/%Y %H:%M:%S')}` • {log.get('message')}"
                    for log in logs
                ]
            ),
            color=self.client.colour,
        )
        embed.set_image(url=self.client.banner_url)
        embed.set_footer(text=self.client.footer_text, icon_url=self.client.user.display_avatar.url)
        return await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Settings(client))
