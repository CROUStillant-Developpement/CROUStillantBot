import discord
import pytz

from ..utils.exceptions import RestaurantIntrouvable, RegionIntrouvable
from ..utils.convert import convertTheme
from ..utils.autocomplete import region_autocomplete, restaurant_autocomplete
from ..utils.date import getCleanDate, getDateFromInput
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Literal


class Commands(commands.Cog):
    """
    Commandes du bot.
    """
    def __init__(self, client: commands.Bot):
        self.client = client


    crous = app_commands.Group(
        name="crous", 
        description="Commandes concernant les restaurants universitaires", 
        allowed_installs=app_commands.AppInstallationType(
            guild=True, 
            user=True
        ), 
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, 
            dm_channel=True, 
            private_channel=True
        )
    )


    # /crous regions

    @crous.command(name="regions", description="Liste des régions disponibles")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def regions(
        self, 
        interaction: discord.Interaction,
    ):
        await interaction.response.defer(thinking=True)

        text = ""
        for region in self.client.cache.regions:
            text += f"` • ` **{region.get('libelle')}**\n"

        embed = discord.Embed(title=f"{len(self.client.cache.regions)} régions disponibles", description=text, color=self.client.colour)
        embed.set_image(url=self.client.banner_url)
        embed.set_footer(text=self.client.footer_text, icon_url=self.client.avatar_url)
        return await interaction.followup.send(embed=embed)


    # /crous restaurants

    @crous.command(name="restaurants", description="Restaurants disponibles par région")
    @app_commands.describe(region="Une région")
    @app_commands.autocomplete(region=region_autocomplete)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def restaurants(
        self, 
        interaction: discord.Interaction,
        region: int
    ):
        await interaction.response.defer(thinking=True)

        region = await self.client.cache.regions.getFromId(region)
        
        if not region:
            raise RegionIntrouvable()

        text = ""
        for restaurant in await self.client.cache.restaurants.getFromRegionID(region.get('idreg')):
            text += f"` • ` **{restaurant.get('nom')}**\n"

        embed = discord.Embed(title=f"Restaurants disponibles pour : {region.get('libelle')}", description=text, color=self.client.colour)
        embed.set_image(url=self.client.banner_url)
        embed.set_footer(text=self.client.footer_text, icon_url=self.client.avatar_url)
        return await interaction.followup.send(embed=embed)

    
    # /crous restaurant

    @crous.command(name="restaurant", description="Informations sur un restaurant")
    @app_commands.describe(restaurant="Un restaurant")
    @app_commands.autocomplete(region=restaurant_autocomplete)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def restaurant(
        self, 
        interaction: discord.Interaction,
        restaurant: int
    ):
        await interaction.response.defer(thinking=True)

        restaurant = await self.client.cache.restaurants.getFromId(restaurant)

        if not restaurant:
            raise RestaurantIntrouvable()

        embed = discord.Embed(title=f"Restaurant : {restaurant.get('nom')}", color=self.client.colour)
        embed.add_field(name="Adresse", value=restaurant.get('adresse'), inline=False)
        embed.add_field(name="Téléphone", value=restaurant.get('telephone'), inline=False)
        embed.add_field(name="Horaires", value=restaurant.get('horaires'), inline=False)
        embed.set_image(url=restaurant.get('image'))
        embed.set_footer(text=self.client.footer_text, icon_url=self.client.avatar_url)
        return await interaction.followup.send(embed=embed)


    # /crous menu

    @crous.command(name="menu", description="Menu disponible")
    @app_commands.describe(restaurant="Un restaurant")
    @app_commands.describe(repas="Un repas (matin, midi, soir) - par défaut : midi")
    @app_commands.describe(theme="Un thème")
    @app_commands.autocomplete(restaurant=restaurant_autocomplete)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def menu(
        self, 
        interaction: discord.Interaction,
        restaurant: int,
        repas: Literal["matin", "midi", "soir"] = "midi",
        theme: Literal["clair", "sombre", "violet"] = "clair",
        date: str = None
    ):
        if not date:
            date = datetime.now(tz=pytz.timezone("Europe/Paris"))
        else:
            try:
                date = getDateFromInput(date)
            except ValueError:
                return await interaction.response.send_message("La date n'est pas au bon format. Essayez `jj-mm-aaaa`.", ephemeral=True)

        await interaction.response.defer(thinking=True)

        restaurant = await self.client.cache.restaurants.getFromId(restaurant)

        if not restaurant:
            raise RestaurantIntrouvable()

        timestamp = datetime.now(tz=pytz.timezone('Europe/Paris')).timestamp()

        embed = discord.Embed(
            title=f"Menu du **`{getCleanDate(date)}`** - {repas.title()}",
            color=self.client.colour,
        )
        embed.set_image(url=f"https://api.croustillant.menu/v1/restaurants/{restaurant.get('rid')}/menu/{date.strftime('%d-%m-%Y')}/image?theme={convertTheme(theme)}&repas={repas}&timestamp={int(timestamp)}")
        embed.set_footer(text=self.client.footer_text, icon_url=self.client.avatar_url)
        await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Commands(client))
