from datetime import datetime
from json import loads
from typing import Literal

import discord
import pytz

from discord import app_commands
from discord.ext import commands

from ..utils.autocomplete import region_autocomplete, restaurant_autocomplete
from ..utils.convert import convert_theme
from ..utils.date import get_date_from_input
from ..utils.exceptions import RegionIntrouvable, RestaurantIntrouvable
from ..views.list import ListView
from ..views.menu import MenuView
from ..views.restaurant import RestaurantView


class Commands(commands.Cog):
    """
    Commandes du bot.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initialise la classe.

        :param client: Le bot.
        :type client: commands.Bot
        """
        self.client = client

    crous = app_commands.Group(
        name="crous",
        description="Commandes concernant les restaurants universitaires",
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
        allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True),
    )

    # /crous regions

    @crous.command(name="regions", description="Liste des régions disponibles")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def regions(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Liste les régions disponibles.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        await interaction.response.defer(thinking=True)

        text = ""
        for region in self.client.cache.regions:
            text += f"` • ` **{region.get('libelle')}**\n"

        return await interaction.followup.send(
            view=ListView(
                client=self.client,
                content=f"### {len(self.client.cache.regions)} régions disponibles\n\n{text}",
            )
        )

    # /crous restaurants

    @crous.command(name="restaurants", description="Restaurants disponibles par région")
    @app_commands.describe(region="Une région")
    @app_commands.autocomplete(region=region_autocomplete)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def restaurants(self, interaction: discord.Interaction, region: int) -> None:
        """
        Liste les restaurants disponibles pour une région.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param region: La région.
        :type region: int
        """
        await interaction.response.defer(thinking=True)

        region = await self.client.cache.regions.get_from_id(region)

        if not region:
            raise RegionIntrouvable()

        text = ""
        for restaurant in await self.client.cache.restaurants.get_from_region_id(region.get("idreg")):
            text += f"` • ` **{restaurant.get('nom')}**\n"

        return await interaction.followup.send(
            view=ListView(
                client=self.client,
                content=f"### Restaurants disponibles pour : {region.get('libelle')}\n\n{text}",
            )
        )

    # /crous restaurant

    @crous.command(name="restaurant", description="Informations sur un restaurant")
    @app_commands.describe(restaurant="Un restaurant")
    @app_commands.autocomplete(restaurant=restaurant_autocomplete)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def restaurant(self, interaction: discord.Interaction, restaurant: int) -> None:
        """
        Donne des informations sur un restaurant.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param restaurant: Le restaurant.
        :type restaurant: int
        """
        await interaction.response.defer(thinking=True)

        restaurant = await self.client.cache.restaurants.get_from_id(restaurant)

        if not restaurant:
            raise RestaurantIntrouvable()

        if restaurant.get("horaires"):
            horaires = loads(restaurant.get("horaires", "[]"))
        else:
            horaires = []

        if restaurant.get("paiement"):
            paiement = loads(restaurant.get("paiement", "[]"))
        else:
            paiement = []

        if restaurant.get("acces"):
            acces = loads(restaurant.get("acces", "[]"))
        else:
            acces = []

        text = f"""
` • ` **Nom** : {restaurant.get("nom")}
` • ` **Adresse** : {restaurant.get("adresse")}
` • ` **Zone** : {restaurant.get("zone") or "Non renseigné"}
` • ` **Téléphone** : {restaurant.get("telephone") or "Non renseigné"}
` • ` **Email** : {restaurant.get("email") or "Non renseigné"}
` • ` **Horaires** : {"; ".join(horaires) if horaires else "Non renseigné"}
` • ` **Paiement** : {"; ".join(paiement) if paiement else "Non renseigné"}
` • ` **Accès** : {"; ".join(acces) if acces else "Non renseigné"}
` • ` **Accès PMR** : {"Oui" if restaurant.get("pmr") else "Non"}
        """

        return await interaction.followup.send(
            view=RestaurantView(
                client=self.client,
                content=f"### Restaurant : {restaurant.get('nom')}\n\n{text}",
                restaurant=restaurant,
            )
        )

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
        date: str = None,
    ) -> None:
        """
        Donne le menu d'un restaurant pour un repas et une date donnés.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param restaurant: Le restaurant.
        :type restaurant: int
        :param repas: Le repas (matin, midi, soir).
        :type repas: Literal["matin", "midi", "soir"]
        :param theme: Le thème (clair, sombre, violet).
        :type theme: Literal["clair", "sombre", "violet"]
        :param date: La date (jj-mm-aaaa) - par défaut : aujourd'hui.
        :type date: str
        """
        if not date:
            date = datetime.now(tz=pytz.timezone("Europe/Paris"))
        else:
            try:
                date = get_date_from_input(date)
            except ValueError:
                return await interaction.response.send_message(
                    "La date n'est pas au bon format. Essayez `jj-mm-aaaa`.",
                    ephemeral=True,
                )

        await interaction.response.defer(thinking=True)

        restaurant = await self.client.cache.restaurants.get_from_id(restaurant)

        if not restaurant:
            raise RestaurantIntrouvable()

        now = datetime.now(tz=pytz.timezone("Europe/Paris"))
        timestamp = now.timestamp()

        # menu = await self.client.entities.menus.get_current(
        #     id=restaurant.get("rid"), date=now,
        # )

        return await interaction.followup.send(
            view=MenuView(
                client=self.client,
                restaurant=restaurant,
                image=f"https://api.croustillant.menu/v1/restaurants/{restaurant.get('rid')}/menu/{date.strftime('%d-%m-%Y')}/image?theme={convert_theme(theme)}&repas={repas}&timestamp={int(timestamp)}",
            )
        )

    # /stats

    @crous.command(name="stats", description="Statistiques du bot")
    @app_commands.describe()
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
    async def stats(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Donne les statistiques du bot.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        await interaction.response.defer(thinking=True)

        stats = await self.client.entities.stats.get()

        text = f"""
` 🌍 ` **`{stats["regions"]:,d}`** régions
` 🍽️ ` **`{stats["restaurants_actifs"]:,d}`** restaurants
` 📋 ` **`{stats["menus"]:,d}`** menus
` 🥗 ` **`{stats["compositions"]:,d}`** compositions
` 🍛 ` **`{stats["plats"]:,d}`** plats différents"""

        return await interaction.followup.send(
            view=ListView(
                client=self.client,
                content=f"### Statistiques\n\n{text}",
            )
        )


async def setup(client: commands.Bot) -> None:
    """
    Ajoute la classe au bot.

    :param client: Le bot.
    :type client: commands.Bot
    """
    await client.add_cog(Commands(client))
