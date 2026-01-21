import discord


class InfoView(discord.ui.LayoutView):
    """
    Vue d'information.
    """

    def __init__(self, client: discord.Client, content: str) -> None:
        """
        Initialise la vue d'information.

        :param client: Le client Discord.
        :type client: discord.Client
        :param content: Le contenu de l'information.
        :type content: str
        """
        super().__init__()
        self.add_item(
            discord.ui.Container(
                discord.ui.Section(content, accessory=discord.ui.Thumbnail(media=client.user.display_avatar.url)),
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=client.banner_url)),
                discord.ui.TextDisplay(content=f"-# *{client.footer_text}*"),
            )
        )
