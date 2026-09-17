import discord

from ..utils.constants import MODES, NOTIFICATIONS, REPAS, THEMES, THEMES_CONFIGURABLES

# Valeur utilisée dans les menus déroulants pour représenter l'absence de valeur (Discord n'accepte pas de valeur vide).
AUCUNE = "aucune"

# États du panneau de gestion.
ETAT_LISTE = "liste"
ETAT_EDITION = "edition"
ETAT_SUPPRESSION = "suppression"
ETAT_RESTAURANT = "restaurant"

# Libellés des champs, utilisés dans les logs du serveur.
CHAMPS = {
    "channel_id": "salon",
    "theme": "thème",
    "repas": "repas",
    "mode": "mode",
    "notification": "notification",
    "ping_role_id": "rôle mentionné",
}


def get_restaurant_nom(restaurant: dict | None, rid: int) -> str:
    """
    Renvoie le nom d'un restaurant, ou un libellé de secours s'il est introuvable.

    :param restaurant: Le restaurant.
    :type restaurant: dict | None
    :param rid: L'ID du restaurant.
    :type rid: int
    :return: Le nom du restaurant.
    :rtype: str
    """
    return restaurant.get("nom") if restaurant else f"Restaurant inconnu ({rid})"


def get_valeur(champ: str, valeur, guild: discord.Guild) -> str:
    """
    Renvoie la valeur d'un champ sous une forme lisible.

    :param champ: Le champ.
    :type champ: str
    :param valeur: La valeur du champ.
    :type valeur: Any
    :param guild: Le serveur.
    :type guild: discord.Guild
    :return: La valeur lisible.
    :rtype: str
    """
    if champ == "channel_id":
        channel = guild.get_channel(valeur)
        return f"#{channel.name}" if channel else str(valeur)
    elif champ == "ping_role_id":
        role = guild.get_role(valeur) if valeur else None
        return role.name if role else "aucun"
    elif champ == "theme":
        return THEMES.get(valeur, valeur)
    elif champ == "repas":
        return REPAS.get(valeur, valeur)
    elif champ == "mode":
        return MODES.get(valeur, valeur)
    elif champ == "notification":
        return NOTIFICATIONS.get(valeur, "Aucune")

    return str(valeur)


class ConfigurationManager:
    """
    État partagé du panneau de gestion des menus automatiques.

    Le panneau est reconstruit à chaque action : les vues sont jetables, seul le manager conserve l'état.
    """

    def __init__(
        self,
        client: discord.Client,
        guild: discord.Guild,
        author_id: int,
        settings: list,
        limite: int,
    ) -> None:
        """
        Initialise le panneau de gestion.

        :param client: Le bot.
        :type client: discord.Client
        :param guild: Le serveur.
        :type guild: discord.Guild
        :param author_id: L'ID de l'utilisateur ayant lancé la commande.
        :type author_id: int
        :param settings: Les configurations du serveur.
        :type settings: list
        :param limite: Le nombre maximum de configurations par serveur.
        :type limite: int
        """
        self.client = client
        self.guild = guild
        self.author_id = author_id
        self.settings = [dict(setting) for setting in settings]
        self.limite = limite

        self.etat = ETAT_LISTE
        self.rid = None
        self.recherche = []
        self.message = None
        self.view = None
        self.interaction = None

    @property
    def selected(self) -> dict | None:
        """
        Renvoie la configuration en cours de gestion.

        :return: La configuration ou None si aucune n'est sélectionnée.
        :rtype: dict | None
        """
        return next((setting for setting in self.settings if setting.get("rid") == self.rid), None)

    async def check(self, interaction: discord.Interaction) -> bool:
        """
        Vérifie que l'utilisateur est bien celui ayant lancé la commande.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :return: True si l'utilisateur peut utiliser le panneau.
        :rtype: bool
        """
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Ce panneau ne vous appartient pas, lancez la commande `/config liste` pour le vôtre.",
                ephemeral=True,
            )
            return False

        return True

    async def refresh(self) -> None:
        """
        Recharge les configurations depuis la base de données.
        """
        settings = await self.client.entities.parametres.get_from_guild_id(self.guild.id)
        self.settings = [dict(setting) for setting in settings]

    async def build(self) -> discord.ui.LayoutView:
        """
        Construit la vue correspondant à l'état actuel du panneau.

        :return: La vue.
        :rtype: discord.ui.LayoutView
        """
        setting = self.selected

        if setting is None and self.etat != ETAT_LISTE:
            self.etat = ETAT_LISTE
            self.rid = None

        if self.etat == ETAT_SUPPRESSION:
            restaurant = await self.client.cache.restaurants.get_from_id(setting.get("rid"))
            return ConfigurationDeleteView(manager=self, setting=setting, restaurant=restaurant)
        elif self.etat == ETAT_RESTAURANT:
            return RestaurantChoiceView(manager=self, setting=setting, restaurants=self.recherche)
        elif self.etat == ETAT_EDITION:
            restaurant = await self.client.cache.restaurants.get_from_id(setting.get("rid"))
            return ConfigurationEditView(manager=self, setting=setting, restaurant=restaurant)

        restaurants = {}
        for config in self.settings:
            restaurants[config.get("rid")] = await self.client.cache.restaurants.get_from_id(config.get("rid"))

        return ConfigurationsView(manager=self, restaurants=restaurants)

    async def render(self, interaction: discord.Interaction) -> None:
        """
        Reconstruit le panneau et met à jour le message.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        view = await self.build()

        if self.view is not None:
            self.view.stop()

        self.view = view

        await interaction.response.edit_message(view=view)

    async def apply(self, interaction: discord.Interaction, **changements) -> None:
        """
        Applique des modifications à la configuration sélectionnée.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param changements: Les champs à modifier.
        :type changements: dict
        """
        setting = self.selected

        if setting is None:
            self.message = "### Configuration introuvable\n\nElle a peut-être été supprimée entre temps."
            return await self.render(interaction)

        nouveau = {**setting, **changements}

        # Discord ne notifie personne lors de l'édition d'un message : la notification et le ping n'ont de sens
        # qu'en mode ` nouveau message `.
        if nouveau.get("mode") == "edition":
            nouveau["notification"] = None
            nouveau["ping_role_id"] = None

        ancien_message_id = setting.get("message_id")
        if nouveau.get("channel_id") != setting.get("channel_id"):
            nouveau["message_id"] = None

        await self.client.entities.parametres.update(
            id=self.guild.id,
            channel_id=nouveau.get("channel_id"),
            message_id=nouveau.get("message_id"),
            rid=setting.get("rid"),
            theme=nouveau.get("theme"),
            repas=nouveau.get("repas"),
            mode=nouveau.get("mode"),
            notification=nouveau.get("notification"),
            ping_role_id=nouveau.get("ping_role_id"),
        )

        # Le salon a changé : l'ancien message ne sera plus jamais mis à jour, on le supprime.
        if nouveau.get("message_id") is None and ancien_message_id:
            await self.delete_message(setting.get("channel_id"), ancien_message_id)

        modifications = ", ".join(
            f"{CHAMPS.get(champ, champ)} : ` {get_valeur(champ, nouveau.get(champ), self.guild)} `"
            for champ in changements
        )

        await self.client.entities.logs.insert(
            self.guild.id,
            self.client.entities.logs.PARAMETRES_MODIFIES,
            f"Modification du menu automatique du restaurant ` {setting.get('rid')} ` ({modifications}).",
        )

        await self.refresh()

        self.message = f"### Configuration mise à jour\n\nNouveau {modifications}"

        return await self.render(interaction)

    async def change_restaurant(self, interaction: discord.Interaction, restaurant: dict) -> None:
        """
        Change le restaurant de la configuration sélectionnée.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param restaurant: Le nouveau restaurant.
        :type restaurant: dict
        """
        setting = self.selected

        if setting is None:
            self.etat = ETAT_LISTE
            self.message = "### Configuration introuvable\n\nElle a peut-être été supprimée entre temps."
            return await self.render(interaction)

        rid = restaurant.get("rid")

        if rid == setting.get("rid"):
            self.etat = ETAT_EDITION
            self.message = "### Aucun changement\n\nCe restaurant est déjà celui de la configuration."
            return await self.render(interaction)

        if await self.client.entities.parametres.check_if_exist(self.guild.id, rid):
            self.etat = ETAT_EDITION
            self.message = f"### Restaurant déjà configuré\n\nUne autre configuration utilise déjà \
**{restaurant.get('nom')}**, supprimez-la avant de réutiliser ce restaurant."
            return await self.render(interaction)

        ancien = await self.client.cache.restaurants.get_from_id(setting.get("rid"))

        await self.client.entities.parametres.update_restaurant(self.guild.id, setting.get("rid"), rid)

        await self.client.entities.logs.insert(
            self.guild.id,
            self.client.entities.logs.PARAMETRES_MODIFIES,
            f"Changement de restaurant du menu automatique : ` {setting.get('rid')} ` -> ` {rid} `.",
        )

        await self.refresh()

        self.rid = rid
        self.etat = ETAT_EDITION
        self.recherche = []
        self.message = f"### Restaurant modifié\n\n` {get_restaurant_nom(ancien, setting.get('rid'))} ` -> \
**{restaurant.get('nom')}**\n\n*Le message existant affichera le menu du nouveau restaurant lors de la prochaine \
mise à jour.*"

        return await self.render(interaction)

    async def delete(self, interaction: discord.Interaction) -> None:
        """
        Supprime la configuration sélectionnée.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        setting = self.selected

        if setting is None:
            self.etat = ETAT_LISTE
            self.message = "### Configuration introuvable\n\nElle a peut-être été supprimée entre temps."
            return await self.render(interaction)

        restaurant = await self.client.cache.restaurants.get_from_id(setting.get("rid"))

        await self.client.entities.parametres.delete(self.guild.id, setting.get("rid"))

        if setting.get("message_id"):
            await self.delete_message(setting.get("channel_id"), setting.get("message_id"))

        await self.client.entities.logs.insert(
            self.guild.id,
            self.client.entities.logs.PARAMETRES_SUPPRIMES,
            f"Suppression du menu automatique du restaurant ` {setting.get('rid')} `.",
        )

        await self.refresh()

        self.rid = None
        self.etat = ETAT_LISTE
        self.message = f"### Configuration supprimée\n\nLe menu automatique de \
**{get_restaurant_nom(restaurant, setting.get('rid'))}** ne sera plus mis à jour."

        return await self.render(interaction)

    async def delete_message(self, channel_id: int, message_id: int) -> None:
        """
        Supprime le message du menu automatique, si possible.

        :param channel_id: L'ID du salon.
        :type channel_id: int
        :param message_id: L'ID du message.
        :type message_id: int
        """
        try:
            channel = self.guild.get_channel(channel_id)

            if channel:
                await channel.get_partial_message(message_id).delete()
        except discord.HTTPException:
            pass


class ConfigurationSelect(discord.ui.Select):
    """
    Menu déroulant de sélection d'une configuration.
    """

    def __init__(self, manager: ConfigurationManager, restaurants: dict) -> None:
        """
        Initialise le menu déroulant.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param restaurants: Les restaurants des configurations, par ID.
        :type restaurants: dict
        """
        self.manager = manager

        options = []
        for setting in manager.settings:
            channel = manager.guild.get_channel(setting.get("channel_id"))

            options.append(
                discord.SelectOption(
                    label=get_restaurant_nom(restaurants.get(setting.get("rid")), setting.get("rid"))[:100],
                    description=f"#{channel.name if channel else 'salon introuvable'} • \
{REPAS.get(setting.get('repas'), setting.get('repas'))} • {THEMES.get(setting.get('theme'), setting.get('theme'))}"[
                        :100
                    ],
                    value=str(setting.get("rid")),
                    emoji="🍽️",
                )
            )

        super().__init__(
            placeholder="Choisissez une configuration à gérer",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Ouvre la configuration sélectionnée.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        self.manager.rid = int(self.values[0])
        self.manager.etat = ETAT_EDITION
        self.manager.message = None

        return await self.manager.render(interaction)


class ConfigurationSelectRow(discord.ui.ActionRow):
    """
    Ligne du menu déroulant de sélection d'une configuration.
    """

    def __init__(self, manager: ConfigurationManager, restaurants: dict) -> None:
        """
        Initialise la ligne.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param restaurants: Les restaurants des configurations, par ID.
        :type restaurants: dict
        """
        super().__init__()
        self.add_item(ConfigurationSelect(manager=manager, restaurants=restaurants))


class ManagedView(discord.ui.LayoutView):
    """
    Vue de base du panneau de gestion, réservée à l'utilisateur ayant lancé la commande.
    """

    def __init__(self, manager: ConfigurationManager) -> None:
        """
        Initialise la vue.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        """
        super().__init__(timeout=300)
        self.manager = manager

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Vérifie que l'utilisateur peut utiliser le panneau.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :return: True si l'utilisateur peut utiliser le panneau.
        :rtype: bool
        """
        return await self.manager.check(interaction)

    async def on_timeout(self) -> None:
        """
        Désactive tous les composants de la vue lors du timeout.
        """
        for child in self.walk_children():
            if isinstance(child, discord.ui.Button) and child.url is not None:
                continue

            if hasattr(child, "disabled"):
                child.disabled = True

        try:
            if self.manager.interaction:
                await self.manager.interaction.edit_original_response(view=self)
        except Exception as e:
            print(f"Error during config view timeout: {self.manager.guild.id} - {e}")
        finally:
            self.stop()


class ConfigurationsView(ManagedView):
    """
    Vue listant les configurations d'un serveur.
    """

    def __init__(self, manager: ConfigurationManager, restaurants: dict) -> None:
        """
        Initialise la vue.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param restaurants: Les restaurants des configurations, par ID.
        :type restaurants: dict
        """
        super().__init__(manager=manager)

        content = f"### Menus automatiques configurés ({len(manager.settings)}/{manager.limite})\n\n"

        if manager.settings:
            for setting in manager.settings:
                channel = manager.guild.get_channel(setting.get("channel_id"))
                role = manager.guild.get_role(setting.get("ping_role_id")) if setting.get("ping_role_id") else None

                content += f"` 🍽️ ` **{get_restaurant_nom(restaurants.get(setting.get('rid')), setting.get('rid'))}** \
— {channel.mention if channel else '` Salon introuvable `'}\n"
                content += f"-# {REPAS.get(setting.get('repas'), setting.get('repas'))} • \
{THEMES.get(setting.get('theme'), setting.get('theme'))} • {MODES.get(setting.get('mode'), setting.get('mode'))} • \
{NOTIFICATIONS.get(setting.get('notification'), 'Aucune')}{f' • {role.mention}' if role else ''}\n"
        else:
            content += "Aucun menu automatique n'est configuré sur ce serveur.\n\nUtilisez `/config menu` pour en \
créer un."

        children = [
            discord.ui.Section(content, accessory=discord.ui.Thumbnail(media=manager.client.user.display_avatar.url))
        ]

        if manager.message:
            children.append(discord.ui.Separator())
            children.append(discord.ui.TextDisplay(content=manager.message))

        if manager.settings:
            children.append(discord.ui.Separator())
            children.append(ConfigurationSelectRow(manager=manager, restaurants=restaurants))

        children.append(discord.ui.MediaGallery(discord.MediaGalleryItem(media=manager.client.banner_url)))
        children.append(discord.ui.TextDisplay(content=f"-# *{manager.client.footer_text}*"))

        self.add_item(discord.ui.Container(*children))


class ParametreSelect(discord.ui.Select):
    """
    Menu déroulant de modification d'un paramètre d'une configuration.
    """

    def __init__(
        self,
        manager: ConfigurationManager,
        champ: str,
        placeholder: str,
        choix: dict,
        valeur,
    ) -> None:
        """
        Initialise le menu déroulant.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param champ: Le champ modifié.
        :type champ: str
        :param placeholder: Le texte affiché.
        :type placeholder: str
        :param choix: Les choix disponibles ({valeur: (libellé, emoji)}).
        :type choix: dict
        :param valeur: La valeur actuelle du champ.
        :type valeur: Any
        """
        self.manager = manager
        self.champ = champ

        super().__init__(
            placeholder=placeholder,
            options=[
                discord.SelectOption(
                    label=libelle,
                    value=cle if cle is not None else AUCUNE,
                    emoji=emoji,
                    default=cle == valeur,
                )
                for cle, (libelle, emoji) in choix.items()
            ],
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Applique la nouvelle valeur.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        valeur = self.values[0]

        if valeur == AUCUNE:
            valeur = None

        return await self.manager.apply(interaction, **{self.champ: valeur})


class ParametreSelectRow(discord.ui.ActionRow):
    """
    Ligne d'un menu déroulant de modification d'un paramètre.
    """

    def __init__(
        self,
        manager: ConfigurationManager,
        champ: str,
        placeholder: str,
        choix: dict,
        valeur,
    ) -> None:
        """
        Initialise la ligne.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param champ: Le champ modifié.
        :type champ: str
        :param placeholder: Le texte affiché.
        :type placeholder: str
        :param choix: Les choix disponibles ({valeur: (libellé, emoji)}).
        :type choix: dict
        :param valeur: La valeur actuelle du champ.
        :type valeur: Any
        """
        super().__init__()
        self.add_item(
            ParametreSelect(
                manager=manager,
                champ=champ,
                placeholder=placeholder,
                choix=choix,
                valeur=valeur,
            )
        )


class SalonSelect(discord.ui.ChannelSelect):
    """
    Menu déroulant de sélection du salon d'une configuration.
    """

    def __init__(self, manager: ConfigurationManager, channel: discord.abc.GuildChannel | None) -> None:
        """
        Initialise le menu déroulant.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param channel: Le salon actuel.
        :type channel: discord.abc.GuildChannel | None
        """
        self.manager = manager

        super().__init__(
            placeholder="Changer de salon",
            channel_types=[discord.ChannelType.text, discord.ChannelType.news],
            min_values=1,
            max_values=1,
            default_values=[channel] if channel else [],
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Applique le nouveau salon.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        return await self.manager.apply(interaction, channel_id=self.values[0].id)


class RoleSelect(discord.ui.RoleSelect):
    """
    Menu déroulant de sélection du rôle mentionné lors des notifications.
    """

    def __init__(self, manager: ConfigurationManager, role: discord.Role | None) -> None:
        """
        Initialise le menu déroulant.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param role: Le rôle actuel.
        :type role: discord.Role | None
        """
        self.manager = manager

        super().__init__(
            placeholder="Changer le rôle mentionné",
            min_values=0,
            max_values=1,
            default_values=[role] if role else [],
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Applique le nouveau rôle.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        return await self.manager.apply(interaction, ping_role_id=self.values[0].id if self.values else None)


class SelectRow(discord.ui.ActionRow):
    """
    Ligne contenant un menu déroulant déjà construit.
    """

    def __init__(self, select: discord.ui.Item) -> None:
        """
        Initialise la ligne.

        :param select: Le menu déroulant.
        :type select: discord.ui.Item
        """
        super().__init__()
        self.add_item(select)


class ConfigurationEditActionRow(discord.ui.ActionRow):
    """
    Boutons de gestion d'une configuration.
    """

    def __init__(self, manager: ConfigurationManager) -> None:
        """
        Initialise les boutons.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        """
        super().__init__()
        self.manager = manager

    @discord.ui.button(label="Changer de restaurant", emoji="🍽️", style=discord.ButtonStyle.primary)
    async def restaurant(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Ouvre la recherche d'un nouveau restaurant.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param button: Le bouton.
        :type button: discord.ui.Button
        """
        return await interaction.response.send_modal(RestaurantModal(manager=self.manager))

    @discord.ui.button(label="Supprimer", emoji="🗑️", style=discord.ButtonStyle.danger)
    async def supprimer(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Demande confirmation avant de supprimer la configuration.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param button: Le bouton.
        :type button: discord.ui.Button
        """
        self.manager.etat = ETAT_SUPPRESSION
        self.manager.message = None

        return await self.manager.render(interaction)

    @discord.ui.button(label="Retour", emoji="↩️", style=discord.ButtonStyle.gray)
    async def retour(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Retourne à la liste des configurations.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param button: Le bouton.
        :type button: discord.ui.Button
        """
        self.manager.etat = ETAT_LISTE
        self.manager.rid = None
        self.manager.message = None

        return await self.manager.render(interaction)


class ConfigurationEditView(ManagedView):
    """
    Vue de gestion d'une configuration.
    """

    def __init__(self, manager: ConfigurationManager, setting: dict, restaurant: dict | None) -> None:
        """
        Initialise la vue.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param setting: La configuration.
        :type setting: dict
        :param restaurant: Le restaurant de la configuration.
        :type restaurant: dict | None
        """
        super().__init__(manager=manager)

        channel = manager.guild.get_channel(setting.get("channel_id"))
        role = manager.guild.get_role(setting.get("ping_role_id")) if setting.get("ping_role_id") else None

        content = f"### {get_restaurant_nom(restaurant, setting.get('rid'))}\n\n"
        content += f"` 💬 ` Salon : {channel.mention if channel else '` Salon introuvable `'}\n"
        content += f"` 🍽️ ` Repas : ` {REPAS.get(setting.get('repas'), setting.get('repas'))} `\n"
        content += f"` 🎨 ` Thème : ` {THEMES.get(setting.get('theme'), setting.get('theme'))} `\n"
        content += f"` ⚙️ ` Mode : ` {MODES.get(setting.get('mode'), setting.get('mode'))} `\n"
        content += f"` 🔔 ` Notification : ` {NOTIFICATIONS.get(setting.get('notification'), 'Aucune')} `\n"
        content += f"` 🏷️ ` Rôle mentionné : {role.mention if role else '` Aucun `'}\n"

        if setting.get("message_id") and channel:
            content += f"` 📩 ` Message : https://discord.com/channels/{manager.guild.id}/{channel.id}/\
{setting.get('message_id')}\n"
        else:
            content += "` 📩 ` Message : ` Pas encore envoyé `\n"

        children = [
            discord.ui.Section(content, accessory=discord.ui.Thumbnail(media=manager.client.user.display_avatar.url))
        ]

        if manager.message:
            children.append(discord.ui.Separator())
            children.append(discord.ui.TextDisplay(content=manager.message))

        children.append(discord.ui.Separator())
        children.append(
            ParametreSelectRow(
                manager=manager,
                champ="repas",
                placeholder="Changer de repas",
                choix={
                    "matin": ("Matin", "🥐"),
                    "midi": ("Midi", "🍽️"),
                    "soir": ("Soir", "🌙"),
                },
                valeur=setting.get("repas"),
            )
        )
        children.append(
            ParametreSelectRow(
                manager=manager,
                champ="theme",
                placeholder="Changer de thème",
                choix={
                    cle: (libelle, emoji)
                    for cle, (libelle, emoji) in {
                        "light": ("Clair", "☀️"),
                        "dark": ("Sombre", "🌘"),
                        "purple": ("Violet", "🟣"),
                    }.items()
                    if cle in THEMES_CONFIGURABLES or cle == setting.get("theme")
                },
                valeur=setting.get("theme"),
            )
        )
        children.append(
            ParametreSelectRow(
                manager=manager,
                champ="mode",
                placeholder="Changer de mode",
                choix={
                    "edition": ("Édition du message", "✏️"),
                    "nouveau_message": ("Nouveau message", "📨"),
                },
                valeur=setting.get("mode"),
            )
        )

        # Discord ne notifie personne lors de l'édition d'un message : notification et ping sont réservés au mode
        # ` nouveau message `.
        if setting.get("mode") == "nouveau_message":
            children.append(
                ParametreSelectRow(
                    manager=manager,
                    champ="notification",
                    placeholder="Changer de notification",
                    choix={
                        None: ("Aucune", "🔕"),
                        "nouveau": ("Nouveau menu", "🔔"),
                        "maj": ("Menu mis à jour", "📢"),
                        "repas": ("Rappel du repas", "🍽️"),
                    },
                    valeur=setting.get("notification"),
                )
            )
            children.append(SelectRow(select=RoleSelect(manager=manager, role=role)))

        children.append(SelectRow(select=SalonSelect(manager=manager, channel=channel)))
        children.append(ConfigurationEditActionRow(manager=manager))
        children.append(discord.ui.MediaGallery(discord.MediaGalleryItem(media=manager.client.banner_url)))
        children.append(discord.ui.TextDisplay(content=f"-# *{manager.client.footer_text}*"))

        self.add_item(discord.ui.Container(*children))


class ConfigurationDeleteActionRow(discord.ui.ActionRow):
    """
    Boutons de confirmation de suppression d'une configuration.
    """

    def __init__(self, manager: ConfigurationManager) -> None:
        """
        Initialise les boutons.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        """
        super().__init__()
        self.manager = manager

    @discord.ui.button(label="Confirmer la suppression", emoji="🗑️", style=discord.ButtonStyle.danger)
    async def confirmer(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Supprime la configuration.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param button: Le bouton.
        :type button: discord.ui.Button
        """
        return await self.manager.delete(interaction)

    @discord.ui.button(label="Annuler", emoji="↩️", style=discord.ButtonStyle.gray)
    async def annuler(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Annule la suppression.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param button: Le bouton.
        :type button: discord.ui.Button
        """
        self.manager.etat = ETAT_EDITION
        self.manager.message = None

        return await self.manager.render(interaction)


class ConfigurationDeleteView(ManagedView):
    """
    Vue de confirmation de suppression d'une configuration.
    """

    def __init__(self, manager: ConfigurationManager, setting: dict, restaurant: dict | None) -> None:
        """
        Initialise la vue.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param setting: La configuration.
        :type setting: dict
        :param restaurant: Le restaurant de la configuration.
        :type restaurant: dict | None
        """
        super().__init__(manager=manager)

        channel = manager.guild.get_channel(setting.get("channel_id"))

        content = f"### Supprimer la configuration ?\n\nLe menu automatique de \
**{get_restaurant_nom(restaurant, setting.get('rid'))}** dans \
{channel.mention if channel else '` Salon introuvable `'} ne sera plus mis à jour.\n\n*Le message du menu sera \
également supprimé. Cette action est irréversible.*"

        self.add_item(
            discord.ui.Container(
                discord.ui.Section(
                    content, accessory=discord.ui.Thumbnail(media=manager.client.user.display_avatar.url)
                ),
                ConfigurationDeleteActionRow(manager=manager),
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=manager.client.banner_url)),
                discord.ui.TextDisplay(content=f"-# *{manager.client.footer_text}*"),
            )
        )


class RestaurantModal(discord.ui.Modal, title="Changer de restaurant"):
    """
    Formulaire de recherche d'un restaurant.
    """

    recherche = discord.ui.TextInput(
        label="Nom ou identifiant du restaurant",
        placeholder="Exemple : Resto U Crous Illkirch",
        min_length=1,
        max_length=100,
    )

    def __init__(self, manager: ConfigurationManager) -> None:
        """
        Initialise le formulaire.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        """
        super().__init__()
        self.manager = manager

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """
        Recherche les restaurants correspondants.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        recherche = self.recherche.value.lower().strip()

        resultats = [
            restaurant
            for restaurant in self.manager.client.cache.restaurants
            if recherche in restaurant.get("nom").lower() or recherche in str(restaurant.get("rid"))
        ][:25]

        if not resultats:
            self.manager.etat = ETAT_EDITION
            self.manager.message = f"### Aucun restaurant trouvé\n\nAucun restaurant ne correspond à \
` {self.recherche.value} `."
        else:
            self.manager.etat = ETAT_RESTAURANT
            self.manager.recherche = resultats
            self.manager.message = None

        return await self.manager.render(interaction)


class RestaurantSelect(discord.ui.Select):
    """
    Menu déroulant de sélection du nouveau restaurant.
    """

    def __init__(self, manager: ConfigurationManager, restaurants: list) -> None:
        """
        Initialise le menu déroulant.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param restaurants: Les restaurants trouvés.
        :type restaurants: list
        """
        self.manager = manager
        self.restaurants = restaurants

        super().__init__(
            placeholder="Choisissez le nouveau restaurant",
            options=[
                discord.SelectOption(
                    label=restaurant.get("nom")[:100],
                    description=(restaurant.get("zone") or restaurant.get("adresse") or "")[:100],
                    value=str(restaurant.get("rid")),
                    emoji="🍽️",
                )
                for restaurant in restaurants
            ],
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Applique le nouveau restaurant.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        """
        rid = int(self.values[0])
        restaurant = next((r for r in self.restaurants if r.get("rid") == rid), None)

        if restaurant is None:
            self.manager.etat = ETAT_EDITION
            self.manager.message = "### Restaurant introuvable\n\nRelancez la recherche."
            return await self.manager.render(interaction)

        return await self.manager.change_restaurant(interaction, restaurant)


class RestaurantChoiceActionRow(discord.ui.ActionRow):
    """
    Bouton de retour de la vue de choix du restaurant.
    """

    def __init__(self, manager: ConfigurationManager) -> None:
        """
        Initialise le bouton.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        """
        super().__init__()
        self.manager = manager

    @discord.ui.button(label="Retour", emoji="↩️", style=discord.ButtonStyle.gray)
    async def retour(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """
        Retourne à la gestion de la configuration.

        :param interaction: L'interaction.
        :type interaction: discord.Interaction
        :param button: Le bouton.
        :type button: discord.ui.Button
        """
        self.manager.etat = ETAT_EDITION
        self.manager.recherche = []
        self.manager.message = None

        return await self.manager.render(interaction)


class RestaurantChoiceView(ManagedView):
    """
    Vue de choix du nouveau restaurant d'une configuration.
    """

    def __init__(self, manager: ConfigurationManager, setting: dict, restaurants: list) -> None:
        """
        Initialise la vue.

        :param manager: Le panneau de gestion.
        :type manager: ConfigurationManager
        :param setting: La configuration.
        :type setting: dict
        :param restaurants: Les restaurants trouvés.
        :type restaurants: list
        """
        super().__init__(manager=manager)

        content = f"### {len(restaurants)} restaurant(s) trouvé(s)\n\nChoisissez le nouveau restaurant du menu \
automatique.\n\n*Les 25 premiers résultats sont affichés, affinez votre recherche si besoin.*"

        self.add_item(
            discord.ui.Container(
                discord.ui.Section(
                    content, accessory=discord.ui.Thumbnail(media=manager.client.user.display_avatar.url)
                ),
                discord.ui.Separator(),
                SelectRow(select=RestaurantSelect(manager=manager, restaurants=restaurants)),
                RestaurantChoiceActionRow(manager=manager),
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=manager.client.banner_url)),
                discord.ui.TextDisplay(content=f"-# *{manager.client.footer_text}*"),
            )
        )
