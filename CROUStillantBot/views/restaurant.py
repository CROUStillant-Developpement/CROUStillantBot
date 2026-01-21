import discord

from ..utils.functions import get_crous_link


class ActionRow(discord.ui.ActionRow):
    """
    Ligne d'actions pour la vue du restaurant.
    """

    def __init__(self, restaurant: dict) -> None:
        """
        Initialise la ligne d'actions.

        :param restaurant: Le restaurant.
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


class RestaurantView(discord.ui.LayoutView):
    """
    Vue du restaurant.
    """

    def __init__(self, client: discord.Client, content: str, restaurant: dict) -> None:
        """
        Initialise la vue.

        :param client: Le bot.
        :type client: discord.Client
        :param content: Le contenu.
        :type content: str
        :param restaurant: Le restaurant.
        :type restaurant: dict
        """
        super().__init__()
        self.add_item(
            discord.ui.Container(
                discord.ui.Section(
                    content,
                    accessory=discord.ui.Thumbnail(media=client.user.display_avatar.url),
                ),
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(media=restaurant.get("image_url", None) or client.banner_url)
                ),
                ActionRow(restaurant=restaurant),
                discord.ui.TextDisplay(content=f"-# *{client.footer_text}*"),
            )
        )
