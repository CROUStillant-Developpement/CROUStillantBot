import discord
import traceback


class BetaEmailModal(discord.ui.Modal, title="Participer au programme beta"):
    email = discord.ui.Label(
        text="Email",
        description="Votre adresse email pour autoriser votre compte à accéder à l'application mobile.",
        component=discord.ui.TextInput(
            style=discord.TextStyle.short,
        ),
        id=1,
    )

    confirmation = discord.ui.Label(
        text="Confirmation",
        description="En validant, vous acceptez l’usage exclusif de votre email pour l’accès à l’app.",
        component=discord.ui.Select(
            options=[
                discord.SelectOption(
                    label="Je refuse",
                    value="decline",
                    description="Vous ne pourrez pas accéder à l'application mobile.",
                    default=True,
                ),
                discord.SelectOption(
                    label="J'accepte, je veux participer au programme beta",
                    value="accept",
                    description="Votre email ne sera pas utilisé à d'autres fins.",
                ),
            ],
            min_values=1,
            max_values=1,
        ),
        id=2,
    )

    def __init__(self) -> None:
        super().__init__(
            custom_id="beta_email_modal",
        )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(1415777875583307798)  # beta

        if self.confirmation.component.values[0] == "decline":
            embed = discord.Embed(
                title="Inscription au programme beta refusée",
                description="Vous avez refusé que votre email soit utilisé pour vous autoriser à accéder à l'application mobile. Votre demande n'a pas été prise en compte.",
                color=0x2F3136,
            )
            embed.set_image(url=interaction.client.banner_url)
            embed.set_footer(
                text=interaction.client.footer_text,
                icon_url=interaction.client.user.display_avatar.url,
            )
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
        else:
            embed = discord.Embed(
                title="Nouvelle inscription au programme beta",
                color=0x2F3136,
            )
            embed.add_field(
                name="Email", value=f"`{self.email.component.value}`", inline=False
            )
            embed.add_field(
                name="Confirmation",
                value="`Accepte`"
                if self.confirmation.component.values[0] == "accept"
                else "`Refuse`",
                inline=False,
            )
            embed.set_image(url=interaction.client.banner_url)
            embed.set_footer(
                text=interaction.client.footer_text,
                icon_url=interaction.client.user.display_avatar.url,
            )
            await channel.send(embed=embed)

            embed = discord.Embed(
                title="Inscription au programme beta réussie",
                description="Merci de vous être inscrit au programme beta ! Votre demande a bien été prise en compte, vous serez notifié lorsque l'application mobile sera disponible.",
                color=0x2F3136,
            )
            embed.set_image(url=interaction.client.banner_url)
            embed.set_footer(
                text=interaction.client.footer_text,
                icon_url=interaction.client.user.display_avatar.url,
            )
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        traceback.print_exc()

        await interaction.response.send_message(
            "Une erreur est survenue.", ephemeral=True
        )
