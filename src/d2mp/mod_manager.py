'''
Created on 01.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QSettings
from os.path import join, exists, normpath, isdir, isfile
from d2mp import STEAM_EXE, DOTA_EXE, log
import os

class ModManager(object):
    
    _instance = None
    
    def __new__(cls, clear_cache = False):
        if not cls._instance: 
            cls._instance = super(ModManager, cls).__new__(cls)
        if clear_cache:
            cls._instance._cache = {}
        return cls._instance
    
    def __init__(self, *args):
        super(ModManager, self).__init__()
        self._cache = {}
        
        self._create_dirs()
        
    def _create_dirs(self):
        for p in [self._d2mp_path(), self._mod_path()]:
            if not isdir(p): os.makedirs(p)
            
    def _steam_path(self):
        if os.name == "nt":
            if self._cache.get("steam_path") is None:
                self._cache["steam_path"] = str(QSettings("HKEY_CURRENT_USER\\Software\\Valve\\Steam", QSettings.NativeFormat).value("SteamPath", "").toString())
            return self._cache["steam_path"]
        else:
            return None
    
    def _dota_path(self):
        dota_loc = [self._steam_path(), "SteamApps", "common"]
        for p in ["dota 2", "dota 2 beta"]:
            if exists("/".join(dota_loc + [p])): return "/".join(dota_loc + [p])
        return None
    
    def _mod_path(self):
        return join(self._addons_path(), "d2moddin")
    
    def _d2mp_path(self):
        return join(self._dota_path(), normpath("dota/d2moddin"))
    
    def _addons_path(self):
        return join(self._dota_path(), normpath("dota/addons"))

    def _delete_all(self, path):
        if not exists(path): return
        for f in os.listdir(path):
            cur_path = join(path, f)
            if isfile(cur_path): os.remove(cur_path)
            else: self._delete_all(cur_path)
        os.rmdir(path)

    def find_steam_exe(self):
        return join(self._steam_path(), STEAM_EXE)
    
    def find_dota_exe(self):
        return join(self._dota_path(), DOTA_EXE)
    
    def _mod_name_file(self):
        return join(self._mod_path(), "modname.txt")
    
    def get_active_mod(self):
        info_file = self._mod_name_file()
        if not isfile(info_file): return None
        name = open(info_file).read()
        log.DEBUG("Current active mod: %s" %name)
        return name

    def install_mod(self, mod_name, url):
        pass

    def delete_mod(self, mod_name):
        pass
    
    def delete_mods(self):
        pass
    
    def _copy(self, from_dir, to_dir):
        pass
    
    def set_mod(self, mod_name):
        active_mod = self.get_active_mod()
        if not(active_mod is None or active_mod != mod_name): return
        self._delete_all(self._mod_path())
        log.DEBUG("Setting active mod to %s."%mod_name);
        self._copy(join(self._d2mp_path(), mod_name.split("=")[0]), self._mod_path())
        f = open(self._mod_name_file(), "w")
        f.write(mod_name)
        f.close()
    
    def _mod_names(self):
        if not self._cache.get('mod_names'):
            names = []
            for f in os.listdir(self._d2mp_path()):
                if not isdir(f): continue
                log.DEBUG("Found mod %s, detecting version..." %(f))
                info_file_path = join(self._d2mp_path(), join(f, "addoninfo.txt"))
                if not isfile(info_file_path): log.DEBUG("no addoninfo file found: %s" %(info_file_path))
                    
                info_file = open(info_file_path, "r")
                info_file_content = info_file.read()
                info_file.close()
            
            if not names: log.ERROR("no mods could be found under %s" %(self._d2mp_path()))
            self._cache['mod_names'] = names
        return self._cache['mod_names']
    
    def show_mod_list(self):
        mod_names = self._mod_names()
        if mod_names:
            msg = "You currently have no mods installed"
        else:
            msg = "You currently have the following detected mods installed:\n\n%s" %(", ".join(self._modNames()))
        return msg

    def mod_game_info(self):
        pass

    def unmod_game_info(self):
        pass
        