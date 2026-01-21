import traceback

from os import environ
from random import choice

import discord

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from ..utils.exceptions import (
    MenuIntrouvable,
    RegionIntrouvable,
    RestaurantIntrouvable,
)
from ..views.error import ErrorView

load_dotenv(dotenv_path=".env")


class Errors(commands.Cog):
    """
    Gestion des erreurs.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client
        self.client.tree.on_error = self.on_app_command_error

        self.commands = None

        self.erreurs = {
            302: [
                "Le serveur a déménagé !",
                "Le restaurant a changé d'adresse !",
            ],
            400: [
                "Le serveur n'a pas compris votre commande !",
                "Introuvable sur le menu !",
            ],
            403: [
                "Dégustation interdite !",
                "Accès refusé, la recette secrete !",
                "La cuisine est réservée aux chefs !",
            ],
            404: [
                "Pâtes bol !",
                "Le chef a tout mangé !",
                "Le plat était froid !",
                "Le serveur ne trouve plus votre table !",
                "La commande s'est perdue en cuisine !",
                "Le chef n'a pas préparé ce plat aujourd'hui !",
                "La table est vide... où est votre assiette ?",
                "Êtes vous sûr d'avoir une réservation ?",
            ],
            409: ["Confit !", "Coincé entre deux plats !", "Deux chefs, une recette !"],
            425: [
                "Ce n'est pas encore l'heure du repas ?!",
            ],
            429: [
                "Le serveur est débordé !",
                "Trop de commandes à la fois !",
                "Le chef est submergé !",
                "Le four est en surchauffe !",
            ],
            500: [
                "Oops... Le serveur s'est trompé de table !",
                "Oops... Le serveur a renversé votre assiette !",
                "Oops... Le serveur a renversé le serveur !",
            ],
        }

    async def on_app_command_error(self, interaction: discord.Interaction, error) -> None:
        """
        Gère les erreurs des commandes.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param error: L'erreur.
        :type error: Exception
        """
        error = getattr(error, "original", error)

        if not self.commands:
            self.commands = await interaction.client.tree.fetch_commands(guild=None)

        for cmd in self.commands:
            try:
                if (
                    cmd.name == interaction.command.name
                    or cmd.name == interaction.command.parent.name
                    or cmd.name == interaction.command.root_parent.name
                ):
                    if isinstance(cmd, discord.app_commands.Group):
                        for c in cmd.commands:
                            if c.name == interaction.command.name:
                                id = cmd.id
                    else:
                        id = cmd.id
                        break
            except Exception:
                continue

        text = None

        if isinstance(error, RegionIntrouvable):
            text = f"## 404 • {choice(self.erreurs[404])}\n\nUne erreur est survenue avec la commande \
</{interaction.command.qualified_name}:{id}> :\n> **Cette région est introuvable !**"
        elif isinstance(error, RestaurantIntrouvable):
            text = f"## 404 • {choice(self.erreurs[404])}\n\nUne erreur est survenue avec la commande \
</{interaction.command.qualified_name}:{id}> :\n> **Ce restaurant est introuvable !**"
        elif isinstance(error, MenuIntrouvable):
            text = f"## 404 • {choice(self.erreurs[404])}\n\nUne erreur est survenue avec la commande \
</{interaction.command.qualified_name}:{id}> :\n> **Le menu est introuvable !**"
        elif isinstance(error, app_commands.errors.CommandOnCooldown):
            text = f"## 429 • {choice(self.erreurs[429])}\n\nUne erreur est survenue avec la commande \
</{interaction.command.qualified_name}:{id}> :\n> **Veuillez ralentir l'envoie des commandes s'il vous \
plaît...**\n> *Vous pouvez relancer la commande dans `{round(error.retry_after, 2)}s`.*"
        elif isinstance(error, app_commands.errors.MissingPermissions):
            text = f"## 403 • {choice(self.erreurs[403])}\n\nUne erreur est survenue avec la commande \
</{interaction.command.qualified_name}:{id}> :\n> **Vous n'avez pas la permission d'utiliser cette commande...**"
        else:
            print(traceback.format_exc())

            if interaction.command:
                text = f"## 500 • {choice(self.erreurs[500])}\n\nUne erreur inconnue est survenue avec la commande \
</{interaction.command.qualified_name}:{id}>...\n> *L'équipe de développement a été prévenue et s'occupe du problème !*"
            else:
                text = f"## 500 • {choice(self.erreurs[500])}\n\nUne erreur inconnue est survenue avec cette \
interaction...\n> *L'équipe de développement a été prévenue et s'occupe du problème !*"

        if text:
            try:
                return await interaction.response.send_message(
                    view=ErrorView(
                        client=self.client,
                        content=text,
                        lien=environ["DISCORD_INVITE_URL"],
                    )
                )
            except discord.errors.InteractionResponded:
                return await interaction.followup.send(
                    view=ErrorView(
                        client=self.client,
                        content=text,
                        lien=environ["DISCORD_INVITE_URL"],
                    )
                )


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Errors(client))
