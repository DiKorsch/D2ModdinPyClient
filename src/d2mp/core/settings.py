'''
Created on 16.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QObject, QSettings, pyqtSignal
from d2mp.utils import log
from os.path import exists, expanduser, isfile, join, normpath
from d2mp import DOTA_EXE, STEAM_EXE
import os
import sys


def is_dota_path_valid(path):
    return isfile(join(path, DOTA_EXE))

def is_steam_path_valid(path):
    return isfile(join(path, STEAM_EXE))

def dota_path_default():
    
    steam = Settings().get(Settings.STEAM_PATH_KEY)
    dota_loc = [steam, "SteamApps", "common"]
    for p in ["dota 2", "dota 2 beta"]:
        if exists("/".join(dota_loc + [p])): return normpath("/".join(dota_loc + [p]))
    
    Settings.dota_missing = True
    log.CRITICAL("No dota2 folder found! Please install it or adjust the settings!")
    return ""

def steam_path_default():
    path = ""
    if os.name == "nt":
        path = str(QSettings("HKEY_CURRENT_USER\\Software\\Valve\\Steam", QSettings.NativeFormat).value("SteamPath", "").toString())
    elif sys.platform == "darwin":
        path = expanduser("~/Library/Application Support/Steam")
    else:
        path = expanduser("~/.steam/steam")
    if not exists(path): 
        log.CRITICAL("No Steam folder found! Please install it or adjust the settings!")
        Settings.steam_missing = True
    return normpath(path)

def only_if_steam_installed(func):
    def wrapper(*args, **kwargs):
        if Settings.steam_missing: 
            print "called %s despite of missing steam" %(str(func))
            return
        return func(*args, **kwargs)
    return wrapper

def only_if_dota_installed(func):
    def wrapper(*args, **kwargs):
        if Settings.dota_missing: 
            print "called %s despite of missing dota" %(str(func))
            return
        return func(*args, **kwargs)
    return wrapper

class Settings(object):
    
    _instance = None
    
    DOTA_PATH_KEY = "dota_path"
    STEAM_PATH_KEY = "steam_path"
    
    steam_missing = False
    dota_missing = False
    
    class signals(QObject):
        changed = pyqtSignal(str, str)
    
    def __new__(cls, clear_cache = False):
        if not cls._instance:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.signals = Settings.signals()
            QSettings.setDefaultFormat(QSettings.IniFormat)
            log.DEBUG("saving settings in file %s" %(QSettings().fileName()));
            cls._instance._settings = QSettings()
            cls._defaults = {
                 Settings.DOTA_PATH_KEY: dota_path_default,
                 Settings.STEAM_PATH_KEY: steam_path_default,
             }
        if clear_cache:
            cls._instance._cache = {}
        return cls._instance
    
    def reset(self):
        for key, default in self._defaults.iteritems():
            self.set(key, default())

    def get(self, setting):
        return str(self._settings.value(setting, self.default(setting)).toString())

    def default(self, key):
        def_func = self._defaults.get(key)
        if def_func is None: return None
        return def_func()
    
    def set(self, setting, value):
        self._settings.setValue(setting, value)
        self.signals.changed.emit(setting, value)