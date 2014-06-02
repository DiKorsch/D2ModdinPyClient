import os

STEAM_EXE = "steam.exe" if os.name == "nt" else "steam"
DOTA_EXE = "dota.exe" if os.name == "nt" else "dota"

SETTINGS = {
    'icon': ':/icon',
    'env': 'dev'
}

GET_ENV = lambda: SETTINGS['env']
