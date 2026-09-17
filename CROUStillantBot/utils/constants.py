CLOCKS = {
    "01:00": "🕐",
    "01:30": "🕜",
    "02:00": "🕑",
    "02:30": "🕝",
    "03:00": "🕒",
    "03:30": "🕞",
    "04:00": "🕓",
    "04:30": "🕟",
    "05:00": "🕔",
    "05:30": "🕠",
    "06:00": "🕕",
    "06:30": "🕡",
    "07:00": "🕖",
    "07:30": "🕢",
    "08:00": "🕗",
    "08:30": "🕣",
    "09:00": "🕘",
    "09:30": "🕤",
    "10:00": "🕙",
    "10:30": "🕥",
    "11:00": "🕚",
    "11:30": "🕦",
    "12:00": "🕛",
    "12:30": "🕧",
}


# Messages de notification pré-définis, envoyés en plus du menu lorsque le contenu (hash) du menu du jour change.
# (Volontairement fermée : pas de texte libre pour éviter les abus.)
NOTIFICATION_MESSAGES = {
    "nouveau": "🔔 Un nouveau menu vient d'être publié !",
    "maj": "📢 Le menu a été mis à jour !",
    "repas": "🍽️ C'est bientôt l'heure, pensez à consulter le menu !",
}


# Libellés des paramètres d'une configuration de menu automatique, tels qu'affichés aux utilisateurs.
THEMES = {
    "light": "Clair",
    "dark": "Sombre",
    "purple": "Violet",
}

REPAS = {
    "matin": "Matin",
    "midi": "Midi",
    "soir": "Soir",
}

MODES = {
    "edition": "Édition du message",
    "nouveau_message": "Nouveau message",
}

NOTIFICATIONS = {
    None: "Aucune",
    "nouveau": "Nouveau menu",
    "maj": "Menu mis à jour",
    "repas": "Rappel du repas",
}

# Thèmes proposés à la configuration, identiques aux choix de ` /config menu `.
THEMES_CONFIGURABLES = ("light", "dark")
