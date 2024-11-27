import discord
import traceback

from ..utils.exceptions import Error, RegionIntrouvable, RestaurantIntrouvable, MenuIntrouvable
from ..utils.views import Lien
from discord import app_commands
from discord.ext import commands
from os import environ
from dotenv import load_dotenv
from random import choice


load_dotenv(dotenv_path=f".env")


class Errors(commands.Cog):
    """
    Gestion des erreurs.
    """
    def __init__(self, client: commands.Bot):
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
                "Introuvable sur le menu !"
            ],
            403: [
                "Dégustation interdite !",
                "Accès refusé, la recette secrete !",
                "La cuisine est réservée aux chefs !"
            ],
            404: [
                "Pâtes bol !",
                "Le chef a tout mangé !",
                "Le plat était froid !",
                "Le serveur ne trouve plus votre table !",
                "La commande s'est perdue en cuisine !",
                "Le chef n'a pas préparé ce plat aujourd'hui !",
                "La table est vide... où est votre assiette ?",
                "Êtes vous sûr d'avoir une réservation ?"
            ],
            409: [
                "Confit !",
                "Coincé entre deux plats !",
                "Deux chefs, une recette !"
            ],
            425: [
                "Ce n'est pas encore l'heure du repas ?!",
            ],
            429: [
                "Le serveur est débordé !",
                "Trop de commandes à la fois !",
                "Le chef est submergé !",
                "Le four est en surchauffe !"
            ],
            500: [
                "Le serveur s'est trompé de table !",
                "le serveur a renversé votre assiette !",
                "Le serveur a renversé le serveur !"
            ]
        }


    async def on_app_command_error(self, interaction: discord.Interaction, error):
        error = getattr(error, 'original', error)

        if self.commands == None:
            self.commands = await interaction.client.tree.fetch_commands(guild=None)

        for cmd in self.commands:
            try:
                if cmd.name == interaction.command.name or cmd.name == interaction.command.parent.name or cmd.name == interaction.command.root_parent.name:
                    if type(cmd) == discord.app_commands.Group:
                        for c in cmd.commands:
                            if c.name == interaction.command.name:
                                id = cmd.id
                    else:
                        id = cmd.id
                        break
            except:
                continue

        embed = None

        if isinstance(error, Error):
            if isinstance(error, RegionIntrouvable):
                embed = discord.Embed(description=f"## 404 - {choice(self.erreurs[404])}\n\nUne erreur est survenue avec la commande </{interaction.command.qualified_name}:{id}> :\n> **Cette région est introuvable !**", color=self.client.colour)     
            elif isinstance(error, RestaurantIntrouvable):
                embed = discord.Embed(description=f"## 404 - {choice(self.erreurs[404])}\n\nUne erreur est survenue avec la commande </{interaction.command.qualified_name}:{id}> :\n> **Ce restaurant est introuvable !**", color=self.client.colour)
            elif isinstance(error, MenuIntrouvable):
                embed = discord.Embed(description=f"## 404 - {choice(self.erreurs[404])}\n\nUne erreur est survenue avec la commande </{interaction.command.qualified_name}:{id}> :\n> **Le menu est indisponible !**", color=self.client.colour)

            if embed:
                embed.set_image(url="https://raw.githubusercontent.com/CROUStillant-Developpement/CROUStillantAssets/main/banner-small.png")
                embed.set_footer(text=self.client.footer_text, icon_url=self.client.avatar_url)
                return await interaction.followup.send(embed=embed, view=Lien("Aide", environ["DISCORD_INVITE_URL"]), ephemeral=True)

        elif isinstance(error, app_commands.errors.CommandOnCooldown):
            embed = discord.Embed(description=f"## 429 - {choice(self.erreurs[429])}\n\nUne erreur est survenue avec la commande </{interaction.command.qualified_name}:{id}> :\n> **Veuillez ralentir l'envoie des commandes s'il vous plaît...**> \n> *Vous pouvez relancer la commande dans `{round(error.retry_after, 2)}s`.*", color=self.client.colour)

        if embed:
            embed.set_image(url="https://raw.githubusercontent.com/CROUStillant-Developpement/CROUStillantAssets/main/banner-small.png")
            embed.set_footer(text=self.client.footer_text, icon_url=self.client.avatar_url)

            try:
                return await interaction.response.send_message(embed=embed, view=Lien("Aide", environ["DISCORD_INVITE_URL"]), ephemeral=True)
            except:
                return await interaction.followup.send(embed=embed, view=Lien("Aide", environ["DISCORD_INVITE_URL"]), ephemeral=True)
        else:
            self.client.logger.error(traceback.format_exc())

            embed = discord.Embed(title="Uh oh !", description=f"Une erreur inconnue est survenue avec la commande </{interaction.command.qualified_name}:{id}>...", color=self.client.colour)
            embed.set_image(url="https://raw.githubusercontent.com/CROUStillant-Developpement/CROUStillantAssets/main/banner-small.png")
            embed.set_footer(text=self.client.footer_text, icon_url=self.client.avatar_url)
            return await interaction.followup.send(embed=embed, view=Lien("Aide", environ["DISCORD_INVITE_URL"]), ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Errors(client))
