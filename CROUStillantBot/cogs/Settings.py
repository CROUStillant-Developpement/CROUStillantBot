from datetime import datetime
from typing import Literal

import discord

from discord import app_commands
from discord.ext import commands

from ..utils.autocomplete import restaurant_autocomplete
from ..utils.functions import get_log_emoji, get_permissions_checklist
from ..views.config import ConfigurationManager
from ..views.info import InfoView
from ..views.list import ListView
from ..views.menu import MenuConfigView


class Settings(commands.Cog):
    """
    Paramètres du bot pour les serveurs.
    """

    MAX_MENUS_AUTOMATIQUES = 5

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

    config = app_commands.Group(name="config", description="Commandes de configuration du bot", guild_only=True)

    # /config menu

    @config.command(name="menu", description="Configuration du menu automatique")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(channel="Un salon")
    @app_commands.describe(restaurant="Un restaurant")
    @app_commands.describe(repas="Un repas (matin, midi, soir) - par défaut : midi")
    @app_commands.describe(theme="Un thème (clair, sombre, violet) - par défaut : clair")
    @app_commands.describe(
        mode="Édition du message existant (défaut) ou nouveau message à chaque mise à jour (nécessaire pour les pings)"
    )
    @app_commands.describe(
        notification="Message envoyé quand le menu du jour est modifié - uniquement en mode ` nouveau message `"
    )
    @app_commands.describe(
        ping_role="Rôle à mentionner lors de la notification - uniquement en mode ` nouveau message `"
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
        mode: Literal["édition", "nouveau message"] = "édition",
        notification: Literal["aucune", "nouveau menu", "menu mis à jour", "rappel du repas"] = "aucune",
        ping_role: discord.Role = None,
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
        :param mode: Édition du message existant ou nouveau message à chaque mise à jour.
        :type mode: Literal["édition", "nouveau message"]
        :param notification: Message pré-défini envoyé lors d'une mise à jour.
        :type notification: Literal["aucune", "nouveau menu", "menu mis à jour", "rappel du repas"]
        :param ping_role: Rôle à mentionner lors de la notification.
        :type ping_role: discord.Role
        """
        await interaction.response.defer(thinking=True)

        if theme == "clair":
            theme = "light"
        elif theme == "sombre":
            theme = "dark"
        elif theme == "violet":
            theme = "purple"

        internal_mode = "nouveau_message" if mode == "nouveau message" else "edition"
        internal_notification = {
            "aucune": None,
            "nouveau menu": "nouveau",
            "menu mis à jour": "maj",
            "rappel du repas": "repas",
        }[notification]

        if internal_mode == "edition" and (internal_notification is not None or ping_role is not None):
            return await interaction.followup.send(
                view=InfoView(
                    client=self.client,
                    content="### Notification impossible en mode ` édition `\n\nDiscord ne notifie personne lorsqu'un \
message existant est modifié, même s'il contient une mention.\n\nPour utiliser une notification et/ou un ping de \
rôle, configurez d'abord `mode: nouveau message`.",
                ),
            )

        ping_role_id = ping_role.id if ping_role else None

        settings = await self.client.entities.parametres.check_if_exist(interaction.guild_id, restaurant)

        if not settings:
            count = await self.client.entities.parametres.count(interaction.guild_id)

            if count >= self.MAX_MENUS_AUTOMATIQUES:
                return await interaction.followup.send(
                    view=InfoView(
                        client=self.client,
                        content="### Limite de configurations atteinte\n\nVous avez atteint la limite de \
configurations pour les menus automatiques.\n\nSupprimez une configuration pour en ajouter une nouvelle.",
                    ),
                )

            await self.client.entities.parametres.insert(
                interaction.guild_id,
                channel.id,
                None,
                restaurant,
                theme,
                repas,
                internal_mode,
                internal_notification,
                ping_role_id,
            )

            await self.client.entities.logs.insert(
                interaction.guild_id,
                self.client.entities.logs.PARAMETRES_MODIFIES,
                f"Configuration du menu automatique pour le restaurant ` {restaurant} ` dans le salon \
` #{channel.name} ` pour le repas du ` {repas} ` avec le thème ` {theme} ` (mode : ` {mode} `).",
            )
        else:
            await self.client.entities.parametres.update(
                interaction.guild_id,
                channel.id,
                settings.get("message_id") if settings.get("channel_id") == channel.id else None,
                restaurant,
                theme,
                repas,
                internal_mode,
                internal_notification,
                ping_role_id,
            )
            await self.client.entities.logs.insert(
                interaction.guild_id,
                self.client.entities.logs.PARAMETRES_MODIFIES,
                f"Mise à jour du menu automatique pour le restaurant ` {restaurant} ` dans le salon \
` #{channel.name} ` pour le repas du {repas} avec le thème ` {theme} ` (mode : ` {mode} `).",
            )

        now = datetime.now()
        if now.hour == 23:
            next_hour = datetime(now.year, now.month, now.day + 1, 0)
        else:
            next_hour = datetime(now.year, now.month, now.day, now.hour + 1, 0)

        diff = next_hour - now
        timestamp = int((now.timestamp() + diff.total_seconds()))

        content1 = "### Configuration du menu automatique réussie\n\nLe menu automatique a été configuré pour le \
restaurant ` {restaurant} `\nDans le salon ` #{channel.name} ` ({channel.mention})\nPour le repas du ` {repas} `\
\nAvec le thème ` {theme} `\nEn mode ` {mode} `".format(
            restaurant=restaurant,
            channel=channel,
            repas=repas,
            theme=theme,
            mode=mode,
        )

        if internal_notification:
            content1 += f"\nAvec la notification ` {notification} `"
            if ping_role:
                content1 += f" en mentionnant {ping_role.mention}"

        permissions = channel.permissions_for(interaction.guild.me)
        content1 += f"\n\n### Permissions du bot dans {channel.mention}\n\
{get_permissions_checklist(interaction.guild, channel)}"

        if not permissions.view_channel or not permissions.send_messages:
            content1 += "\n\n-# ⚠️ *Le bot ne pourra pas envoyer le menu tant que ces permissions ne sont pas \
accordées.*"

        return await interaction.followup.send(
            view=MenuConfigView(
                client=self.client,
                content1=content1,
                content2=f"### Informations\n\nLe menu est vérifié toutes les heures et mis à jour automatiquement \
lorsqu'il change.\n\n**La première mise à jour aura lieu <t:{timestamp}:R> (<t:{timestamp}>).**\n\n*En cas de \
suppression du message ou du salon, la configuration sera automatiquement supprimée.*",
            )
        )

    # /config liste

    @config.command(name="liste", description="Voir et gérer les menus automatiques configurés")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def liste(self, interaction: discord.Interaction) -> None:
        """
        Affiche les menus automatiques configurés et permet de les gérer.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        await interaction.response.defer(thinking=True, ephemeral=True)

        settings = await self.client.entities.parametres.get_from_guild_id(interaction.guild_id)

        if not settings:
            return await interaction.followup.send(
                view=InfoView(
                    client=self.client,
                    content="### Aucune configuration\n\nAucun menu automatique n'est configuré sur ce \
serveur.\n\nUtilisez ` /config menu ` pour en créer un.",
                ),
            )

        manager = ConfigurationManager(
            client=self.client,
            guild=interaction.guild,
            author_id=interaction.user.id,
            settings=settings,
            limite=self.MAX_MENUS_AUTOMATIQUES,
        )
        manager.interaction = interaction
        manager.view = await manager.build()

        return await interaction.followup.send(view=manager.view)

    # /config logs

    @config.command(name="logs", description="Voir les logs du serveur")
    @app_commands.describe(page="Numéro de la page")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def logs(self, interaction: discord.Interaction, page: int = 1) -> None:
        """
        Envoie les logs du serveur.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param page: Le numéro de la page.
        :type page: int
        """
        await interaction.response.defer(thinking=True)

        logs = await self.client.entities.logs.get_last(interaction.guild.id, 20, offset=(page - 1) * 20)
        if not logs:
            return await interaction.followup.send(
                view=InfoView(
                    client=self.client,
                    content="### Logs introuvables\n\nAucun log n'a été trouvé pour ce serveur.",
                )
            )
        else:
            return await interaction.followup.send(
                view=ListView(
                    client=self.client,
                    content="### Logs du serveur\n\n"
                    + "\n".join(
                        [
                            f"{get_log_emoji(log.get('idtpl'))} `{log.get('log_date').strftime('%d/%m/%Y %H:%M:%S')}` \
• {log.get('message')}"
                            for log in logs
                        ]
                    ),
                )
            )

    # /config debug

    @config.command(name="debug", description="Vérifie les permissions du bot pour les menus automatiques configurés")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def debug(self, interaction: discord.Interaction) -> None:
        """
        Vérifie que le bot a accès aux salons configurés et peut y envoyer des messages.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        await interaction.response.defer(thinking=True, ephemeral=True)

        settings = await self.client.entities.parametres.get_from_guild_id(interaction.guild_id)

        if not settings:
            return await interaction.followup.send(
                view=InfoView(
                    client=self.client,
                    content="### Aucune configuration\n\nAucun menu automatique n'est configuré sur ce \
serveur.\n\nUtilisez ` /config menu ` pour en créer un.",
                ),
            )

        content = "### Diagnostic des menus automatiques\n\n"

        for setting in settings:
            restaurant = await self.client.cache.restaurants.get_from_id(setting.get("rid"))
            channel = interaction.guild.get_channel(setting.get("channel_id"))
            nom = restaurant.get("nom") if restaurant else f"Restaurant inconnu ({setting.get('rid')})"

            content += f"` 🍽️ ` **{nom}** — {channel.mention if channel else '` Salon introuvable `'}\n"
            content += get_permissions_checklist(interaction.guild, channel) + "\n\n"

        return await interaction.followup.send(
            view=ListView(
                client=self.client,
                content=content.strip(),
            )
        )


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Settings(client))
