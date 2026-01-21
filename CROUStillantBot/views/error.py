import discord


class ActionRow(discord.ui.ActionRow):
    """
    Bouton d'aide.
    """

    def __init__(self, lien: dict) -> None:
        """
        Initialise le bouton d'aide.

        :param lien: Le lien d'aide.
        :type lien: dict
        """
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="Obtenir de l'aide",
                style=discord.ButtonStyle.link,
                url=lien,
            )
        )


class ErrorView(discord.ui.LayoutView):
    """
    Vue d'erreur.
    """

    def __init__(self, client: discord.Client, content: str, lien: str) -> None:
        """
        Initialise la vue d'erreur.

        :param client: Le client Discord.
        :type client: discord.Client
        :param content: Le contenu de l'erreur.
        :type content: str
        :param lien: Le lien d'aide.
        :type lien: str
        """
        super().__init__()
        self.add_item(
            discord.ui.Container(
                discord.ui.Section(content, accessory=discord.ui.Thumbnail(media=client.user.display_avatar.url)),
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=client.banner_url)),
                ActionRow(lien=lien),
                discord.ui.TextDisplay(content=f"-# *{client.footer_text}*"),
            )
        )
