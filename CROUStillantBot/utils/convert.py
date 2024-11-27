def convertTheme(theme: str) -> str:
    THEMES = {
        "clair": "light",
        "sombre": "dark"
    }
    
    return THEMES.get(theme, None)
