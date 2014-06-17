import os, sys

if os.name == "nt":
    STEAM_EXE = "steam.exe"
    DOTA_EXE = "dota.exe"
elif sys.platform == "darwin":
    STEAM_EXE = "Steam.app"
    DOTA_EXE = "Dota.app"
else:
    STEAM_EXE = "steam"
    DOTA_EXE = "dota"

SETTINGS = {
    'icon': ':/icon',
    'env': 'dev'
}

GET_ENV = lambda: SETTINGS['env']
