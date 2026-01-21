def convert_theme(theme: str) -> str:
    """
    Convertit un thème en un thème valide pour l'API.

    :param theme: Le thème à convertir.
    :type theme: str
    :return: Le thème converti.
    :rtype: str
    """
    return {
        "clair": "light",
        "sombre": "dark",
        "violet": "purple",
    }.get(theme, "light")
