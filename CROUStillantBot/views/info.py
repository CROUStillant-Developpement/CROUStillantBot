import discord


class InfoView(discord.ui.LayoutView):
    def __init__(self, client: discord.Client, content: str) -> None:
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
                discord.ui.TextDisplay(content=f"-# *{client.footer_text}*")
            )
        )
