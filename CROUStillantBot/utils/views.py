import discord
import traceback

from .date import getCleanDate
from datetime import datetime


class Lien(discord.ui.View):
    """
    Bouton de lien
    """

    def __init__(self, label: str, url: str) -> None:
        """
        Bouton de lien

        :param label: Texte du bouton
        :type label: str
        :param url: URL du bouton
        :type url: str
        """
        super().__init__()

        self.add_item(
            discord.ui.Button(
                label=label, url=url, emoji="<:unknown:1223283454901489756>"
            )
        )


class SelectMenu(discord.ui.Select):
    def __init__(
        self,
        restaurant: dict,
        menus: list,
        theme: str,
        options: list,
        map: str,
        link: tuple[str, str],
    ) -> None:
        """
        Menu déroulant de sélection de menu

        :param restaurant: Dictionnaire du restaurant
        :type restaurant: dict
        :param menus: Liste des menus
        :type menus: list
        :param theme: Thème de l'image (light ou dark)
        :type theme: str
        :param options: Options du menu déroulant
        :type options: list
        :param map: Lien vers la carte du restaurant
        :type map: str
        :param link: Lien vers le site du restaurant
        :type link: tuple[str, str]
        """
        self.restaurant = restaurant
        self.menus = menus
        self.theme = theme
        self.options_list = options
        self.map = map
        self.link = link

        if len(options) > 0:
            super().__init__(
                placeholder="Choisissez un menu",
                options=options,
                min_values=1,
                max_values=1,
                row=0,
            )
        else:
            super().__init__(
                placeholder="Aucun menu disponible",
                options=[
                    discord.SelectOption(
                        label="Aucun menu disponible",
                        value="null",
                        emoji="<:unknown:1223283454901489756>",
                        default=True,
                    )
                ],
                min_values=1,
                max_values=1,
                row=0,
            )

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback du menu déroulant

        :param interaction: Interaction
        :type interaction: discord.Interaction
        """
        try:
            datetime.strptime(self.values[0], "%d-%m-%Y")
            date = self.values[0]
        except ValueError:
            await interaction.response.send_message(
                content="Erreur lors de la récupération du menu", ephemeral=True
            )
            return

        m_saved = None
        for menu in self.menus:
            if menu.get("date").strftime("%d-%m-%Y") == date:
                m_saved = menu
                break

        view = MenuView(
            restaurant=self.restaurant,
            menu=m_saved,
            menus=self.menus,
            options=self.options_list,
            map=self.map,
            link=self.link,
            interaction=interaction,
            ephemeral=True,
        )

        embed = discord.Embed(
            title=f"Menu du **`{getCleanDate(datetime.strptime(date, '%d-%m-%Y'))}`**",
            color=interaction.client.colour,
        )
        embed.set_image(
            url=f"https://api.croustillant.menu/v1/restaurants/{self.restaurant.get('rid')}/menu/{date}/image?theme={self.theme}&timestamp={int(datetime.now().timestamp())}"
        )
        embed.set_footer(
            text=interaction.client.footer_text, icon_url=interaction.client.avatar_url
        )
        await interaction.response.send_message(embed=embed, ephemeral=True, view=view)


class MenuView(discord.ui.View):
    """
    Bouton de menu
    """

    def __init__(
        self,
        restaurant: dict,
        menu: dict,
        menus: list,
        options: list,
        map: str,
        link: tuple[str, str],
        interaction: discord.Interaction = None,
        ephemeral: bool = False,
    ) -> None:
        """
        Vue du menu

        :param restaurant: Dictionnaire du restaurant
        :type restaurant: dict
        :param menu: Dictionnaire du menu
        :type menu: dict
        :param menus: Liste des menus
        :type menus: list
        :param options: Options du menu déroulant
        :type options: list
        :param map: Lien vers la carte du restaurant
        :type map: str
        :param link: Lien vers le site du restaurant
        :type link: tuple[str, str]
        :param interaction: Interaction, defaults to None
        :type interaction: discord.Interaction, optional
        :param ephemeral: Si le message est éphémère, defaults to False
        :type ephemeral: bool, optional
        """
        super().__init__(timeout=300 if interaction else None)
        self.restaurant = restaurant
        self.menu = menu
        self.menus = menus
        self.options = options
        self.map = map
        self.link = link
        self.interaction = interaction

        self.add_item(
            discord.ui.Button(
                label="M'y rendre", url=map, emoji="<:map:1223283452737224935>", row=1
            )
        )
        self.add_item(
            discord.ui.Button(
                label=link[0],
                url=self.link[1],
                emoji="<:CROUStillantLogo:1223286294612938776>",
                row=1,
            )
        )

        if not ephemeral:
            self.add_item(
                SelectMenu(
                    restaurant=restaurant,
                    menus=menus,
                    theme="light",
                    options=options,
                    map=map,
                    link=link,
                )
            )

    @discord.ui.button(
        emoji="<:list:1223283450904317962>",
        label="Menu",
        style=discord.ButtonStyle.gray,
        row=1,
    )
    async def menuButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """
        Affiche le menu

        :param interaction: Interaction
        :type interaction: discord.Interaction
        :param button: Bouton
        :type button: discord.ui.Button
        """
        try:
            if not self.menu:
                embed = discord.Embed(
                    title=f"Menu du **`{getCleanDate(datetime.now())}`**",
                    description="Aucun menu disponible...",
                    color=interaction.client.colour,
                )
                embed.set_image(url=interaction.client.banner_url)
                embed.set_footer(
                    text=interaction.client.footer_text,
                    icon_url=interaction.client.avatar_url,
                )
            else:
                menu = await interaction.client.entities.menus.getFromDate(
                    id=self.restaurant.get("rid"), date=self.menu.get("date")
                )

                menu_per_day = {}
                for row in menu:
                    date = row.get("date").strftime("%d-%m-%Y")

                    day_menu = menu_per_day.setdefault(
                        date, {"code": row.get("mid"), "date": date, "repas": []}
                    )

                    repas_list = day_menu["repas"]

                    if not repas_list or row.get("tpr") not in repas_list[-1]["type"]:
                        repas_list.append(
                            {
                                "code": row.get("rpid"),
                                "type": row.get("tpr"),
                                "categories": [],
                            }
                        )

                    repas = repas_list[-1]
                    categories_list = repas["categories"]

                    if (
                        not categories_list
                        or row.get("tpcat") not in categories_list[-1]["libelle"]
                    ):
                        categories_list.append(
                            {
                                "code": row.get("catid"),
                                "libelle": row.get("tpcat"),
                                "ordre": row.get("cat_ordre") + 1,
                                "plats": [],
                            }
                        )

                    categories_list[-1]["plats"].append(
                        {
                            "code": row.get("platid"),
                            "ordre": row.get("plat_ordre") + 1,
                            "libelle": row.get("plat"),
                        }
                    )

                embed = discord.Embed(
                    description=f"Menu du **`{getCleanDate(datetime.strptime(self.menu.get('date').strftime('%d-%m-%Y'), '%d-%m-%Y'))}`**",
                    color=interaction.client.colour,
                )

                for meal in menu_per_day[
                    self.menu.get("date").strftime("%d-%m-%Y")
                ].get("repas"):
                    count = 0
                    for category in meal.get("categories"):
                        text = ""

                        for dish in category.get("plats"):
                            if not dish.get("libelle") == "":
                                text += f"• {dish.get('libelle')}\n"

                        embed.add_field(
                            name=category.get("libelle"), value=text, inline=False
                        )
                        count += 1

                        if len(meal.get("categories")) > 25 and count == 24:
                            embed.add_field(
                                name="\u2060",
                                value=f"Et {len(meal.get('categories')) - count} autres categories",
                                inline=False,
                            )
                            break

                    break

            embed.set_image(url=interaction.client.banner_url)
            embed.set_thumbnail(url=self.restaurant.get("image_url"))
            embed.set_footer(
                text=interaction.client.footer_text,
                icon_url=interaction.client.avatar_url,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error during menu display: {self.restaurant.get('rid')} - {e}")
            print(traceback.format_exc())

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.url is not None:
                pass
            else:
                child.disabled = True

        try:
            await self.interaction.edit_original_response(view=self)
        except Exception:
            pass
        finally:
            self.stop()
