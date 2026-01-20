import discord


class ActionRow(discord.ui.ActionRow):
    def __init__(self, restaurant: dict) -> None:
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
                url=f"https://croustillant.menu/fr/restaurants/{restaurant.get('rid')}",
            )
        )


class RestaurantView(discord.ui.LayoutView):
    def __init__(self, client: discord.Client, content: str, restaurant: dict) -> None:
        super().__init__()
        self.add_item(
            discord.ui.Container(
                discord.ui.Section(
                    content,
                    accessory=discord.ui.Thumbnail(
                        media=client.user.display_avatar.url
                    ),
                ),
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(media=restaurant.get("image_url", None) or client.banner_url)
                ),
                ActionRow(restaurant=restaurant),
                discord.ui.TextDisplay(content=f"-# *{client.footer_text}*")
            )
        )
