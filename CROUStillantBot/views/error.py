import discord


class ActionRow(discord.ui.ActionRow):
    def __init__(self, lien: dict) -> None:
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="Obtenir de l'aide",
                style=discord.ButtonStyle.link,
                url=lien,
            )
        )

class ErrorView(discord.ui.LayoutView):
    def __init__(self, client: discord.Client, content: str, lien: str) -> None:
        super().__init__()
        self.add_item(
            discord.ui.Container(
                discord.ui.Section(
                    content,
                    accessory=discord.ui.Thumbnail(media=client.user.display_avatar.url)
                ),
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(media=client.banner_url)
                ),
                ActionRow(lien=lien),
                discord.ui.TextDisplay(content=f"-# *{client.footer_text}*")
            )
        )
