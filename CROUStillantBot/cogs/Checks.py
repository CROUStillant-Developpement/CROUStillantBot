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
    def __init__(self, client: commands.Bot):
        self.client = client
        self.client.tree.interaction_check = self.interaction_check


    async def interaction_check(self, interaction: discord.Interaction):
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

                embed=discord.Embed(title=f"Maintenance", description=f"Hey {interaction.user.mention} ! CROUStillant est en maintenance, réessayez plus tard... \n\nExcusez-nous pour la gêne occasionnée.", color=interaction.client.color)
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
                embed.set_footer(text=interaction.client.footer_text, icon_url=interaction.client.avatar_url) 
            elif not self.client.ready:
                embed=discord.Embed(title=f"Chargement...", description=f"Hey {interaction.user.mention} ! CRONStillant est en train de démarrer, réessayez dans quelques secondes...", color=interaction.client.color)
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
                embed.set_footer(text=interaction.client.footer_text, icon_url=interaction.client.avatar_url)

            if embed:
                try:
                    await interaction.response.send_message(embed=embed, view=Lien("Aide", environ["DISCORD_INVITE_URL"]), ephemeral=True)
                except:
                    pass

                return False
            else:
                self.client.logger.info(f"/{interaction.command.qualified_name} - {interaction.user} ({interaction.user.id})")
                return True
        else:
            if self.client.maintenance or not self.client.ready:
                return False
            else:
                return True


async def setup(client: commands.Bot):
    await client.add_cog(Checks(client))
