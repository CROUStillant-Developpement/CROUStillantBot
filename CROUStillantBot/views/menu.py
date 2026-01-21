from datetime import datetime

import discord
import pytz

from ..utils.date import get_clean_date
from ..utils.functions import get_clock_emoji, get_crous_link
from ..views.list import ListView


class MenuTaskViewButtons(discord.ui.ActionRow):
    """
    Boutons de la vue du menu pour les tâches.
    """

    def __init__(self, restaurant: dict) -> None:
        """
        Initialise les boutons de la vue du menu pour les tâches.

        :param restaurant: Dictionnaire du restaurant
        :type restaurant: dict
        """
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="M'y rendre",
                style=discord.ButtonStyle.link,
                url=f"https://www.google.fr/maps/dir/{restaurant.get('latitude')},{restaurant.get('longitude')}/@{restaurant.get('latitude')},{restaurant.get('longitude')},18.04",
            )
        )

        self.add_item(
            discord.ui.Button(
                label="Voir sur https://croustillant.menu",
                style=discord.ButtonStyle.link,
                url=get_crous_link(restaurant)[1],
            )
        )


class MenuView(discord.ui.LayoutView):
    """
    Vue du menu.
    """

    def __init__(self, client: discord.Client, restaurant: dict, image: str) -> None:
        """
        Initialise la vue du menu.

        :param client: Le client Discord.
        :type client: discord.Client
        :param restaurant: Dictionnaire du restaurant
        :type restaurant: dict
        :param image: URL de l'image
        :type image: str
        """
        super().__init__()
        self.add_item(
            discord.ui.Container(
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=image)),
                MenuTaskViewButtons(restaurant=restaurant),
                discord.ui.TextDisplay(content=f"-# *{client.footer_text}*"),
            )
        )


class MenuConfigView(discord.ui.LayoutView):
    """
    Vue de configuration du menu.
    """

    def __init__(self, client: discord.Client, content1: str, content2: str) -> None:
        """
        Initialise la vue de configuration du menu.

        :param client: Le client Discord.
        :type client: discord.Client
        :param content1: Le premier contenu.
        :type content1: str
        :param content2: Le second contenu.
        :type content2: str
        """
        super().__init__()
        self.add_item(
            discord.ui.Container(
                discord.ui.Section(content1, accessory=discord.ui.Thumbnail(media=client.user.display_avatar.url)),
            )
        )
        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(content2),
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=client.banner_url)),
                discord.ui.TextDisplay(content=f"-# *{client.footer_text}*"),
            )
        )


class MenuTaskViewSelectMenu(discord.ui.Select):
    """
    Menu déroulant de sélection de menu.
    """

    def __init__(
        self,
        restaurant: dict,
        menus: list,
        theme: str,
        options: list,
        get_menu: callable,
        repas: str,
        client: discord.Client,
    ) -> None:
        """
        Menu déroulant de sélection de menu.

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
        self.get_menu = get_menu
        self.repas = repas
        self.client = client

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
        Callback du menu déroulant.

        :param interaction: Interaction
        :type interaction: discord.Interaction
        """
        try:
            datetime.strptime(self.values[0], "%d-%m-%Y")
            date = self.values[0]
        except ValueError:
            await interaction.response.send_message(content="Erreur lors de la récupération du menu", ephemeral=True)
            return

        m_saved = None
        for menu in self.menus:
            if menu.get("date").strftime("%d-%m-%Y") == date:
                m_saved = menu
                break

        view = MenuTaskView(
            restaurant=self.restaurant,
            menu=await self.get_menu(self.restaurant, m_saved) if m_saved else "Aucun menu disponible pour cette date.",
            get_menu=self.get_menu,
            menus=self.menus,
            theme=self.theme,
            repas=self.repas,
            options=self.options_list,
            client=self.client,
            interaction=interaction,
            ephemeral=True,
            selected_date=datetime.strptime(date, "%d-%m-%Y"),
        )

        await interaction.response.send_message(view=view, ephemeral=True)


class MenuTaskViewActionRow(discord.ui.ActionRow):
    """
    Action row de la vue du menu pour les tâches.
    """

    def __init__(
        self,
        restaurant: dict,
        menus: list,
        options: list,
        get_menu: callable,
        ephemeral: bool = False,
        repas: str = "",
        client: discord.Client = None,
    ) -> None:
        """
        Initialise l'action row de la vue du menu pour les tâches.

        :param restaurant: Dictionnaire du restaurant
        :type restaurant: dict
        :param menus: Liste des menus
        :type menus: list
        :param options: Options du menu déroulant
        :type options: list
        :param ephemeral: Si le message est éphémère, defaults to False
        :type ephemeral: bool, optional
        :param repas: Repas sélectionné, defaults to
        :type repas: str, optional
        :param client: Le client Discord.
        :type client: discord.Client
        """
        super().__init__()
        if not ephemeral:
            self.add_item(
                MenuTaskViewSelectMenu(
                    restaurant=restaurant,
                    menus=menus,
                    theme="light",
                    options=options,
                    get_menu=get_menu,
                    repas=repas,
                    client=client,
                )
            )


class MenuTaskViewMenuActionRow(discord.ui.ActionRow):
    """
    Action row de la vue du menu pour les tâches.
    """

    def __init__(
        self,
        menu: str = None,
    ) -> None:
        """
        Initialise l'action row de la vue du menu pour les tâches.

        :param menu: Menu en texte
        :type menu: str
        """
        super().__init__()
        self.menu = menu

    @discord.ui.button(emoji="📄", label="Menu (version texte)", style=discord.ButtonStyle.gray, row=1)
    async def menu_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Bouton pour renvoyer le menu.

        :param button: Le bouton
        :type button: discord.ui.Button
        :param interaction: L'interaction
        :type interaction: discord.Interaction
        """
        view = ListView(
            client=interaction.client,
            content=self.menu,
        )

        return await interaction.response.send_message(view=view, ephemeral=True)


class MenuTaskView(discord.ui.LayoutView):
    """
    Vue du menu pour les tâches.
    """

    def __init__(
        self,
        restaurant: dict,
        menu: str,
        get_menu: callable,
        menus: list,
        theme: str,
        repas: str,
        options: list,
        client: discord.Client = None,
        interaction: discord.Interaction = None,
        ephemeral: bool = False,
        selected_date: datetime = None,
    ) -> None:
        """
        Vue du menu pour les tâches.

        :param restaurant: Dictionnaire du restaurant
        :type restaurant: dict
        :param menu: Dictionnaire du menu
        :type menu: dict
        :param get_menu: Fonction pour le menu sous forme de texte
        :type get_menu: callable
        :param menus: Liste des menus
        :type menus: list
        :param theme: Theme
        :type theme: str
        :param repas: Repas
        :type repas: str
        :param options: Options du menu déroulant
        :type options: list
        :param client: Instance du bot
        :type client: discord.Client
        :param interaction: Interaction
        :type interaction: discord.Interaction, optional
        :param ephemeral: Si le message est éphémère, defaults to False
        :type ephemeral: bool, optional
        :param selected_date: Date sélectionnée
        :type selected_date: datetime
        """
        super().__init__(timeout=300 if ephemeral else None)

        self.restaurant = restaurant
        self.interaction = interaction
        self.get_menu = get_menu

        date = selected_date if selected_date else datetime.now(tz=pytz.timezone("Europe/Paris"))
        emoji = get_clock_emoji(date)
        timestamp = int(date.timestamp())

        content = f"# {restaurant.get('nom')} ({'Ouvert' if restaurant.get('opened') else 'Fermé'})\n"
        content += f"` 📅 ` Menu du **`{get_clean_date(date)}`**\n"
        content += f"` 🍽️ ` Repas sélectionné : **`{repas.capitalize()}`**\n"

        if restaurant.get("adresse"):
            content += f"` 📍 ` Adresse : **`{restaurant.get('adresse')}`**\n"

        if not ephemeral:
            content += f"\n` {emoji} ` **Mis à jour le <t:{timestamp}:R> (<t:{timestamp}>)**"

        content += "\nㅤ"

        self.add_item(
            discord.ui.Container(
                discord.ui.Section(
                    "".join(content), accessory=discord.ui.Thumbnail(media=client.user.display_avatar.url)
                ),
                MenuTaskViewButtons(restaurant=restaurant),
            )
        )

        if ephemeral:
            self.add_item(
                discord.ui.Container(
                    discord.ui.MediaGallery(
                        discord.MediaGalleryItem(
                            media=f"https://api.croustillant.menu/v1/restaurants/{restaurant.get('rid')}/menu/{date.strftime('%d-%m-%Y')}/image?theme={theme}&repas={repas}&timestamp={timestamp}"
                        )
                    ),
                    discord.ui.Separator(),
                    MenuTaskViewMenuActionRow(
                        menu=menu,
                    ),
                    discord.ui.MediaGallery(discord.MediaGalleryItem(media=client.banner_url)),
                    discord.ui.TextDisplay(content=f"-# *{client.footer_text}*"),
                )
            )
        else:
            self.add_item(
                discord.ui.Container(
                    discord.ui.MediaGallery(
                        discord.MediaGalleryItem(
                            media=f"https://api.croustillant.menu/v1/restaurants/{restaurant.get('rid')}/menu/{date.strftime('%d-%m-%Y')}/image?theme={theme}&repas={repas}&timestamp={timestamp}"
                        )
                    ),
                    discord.ui.Separator(),
                    MenuTaskViewActionRow(
                        restaurant=restaurant,
                        ephemeral=ephemeral,
                        menus=menus,
                        options=options,
                        get_menu=get_menu,
                        repas=repas,
                        client=client,
                    ),
                    MenuTaskViewMenuActionRow(
                        menu=menu,
                    ),
                    discord.ui.MediaGallery(discord.MediaGalleryItem(media=client.banner_url)),
                    discord.ui.TextDisplay(content=f"-# *{client.footer_text}*"),
                )
            )

    async def on_timeout(self) -> None:
        """
        Désactive tous les composants de la vue lors du timeout.
        """
        for child in self.walk_children():
            if isinstance(child, discord.ui.Button) and child.url is not None:
                pass
            else:
                child.disabled = True

        try:
            if self.interaction:
                await self.interaction.edit_original_response(view=self)
        except Exception as e:
            print(f"Error during menu task view timeout: {self.restaurant.get('rid')} - {e}")
            pass
        finally:
            self.stop()
