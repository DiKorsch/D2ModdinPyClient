'''
Created on 01.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QSettings
from os.path import join, exists, normpath, isdir, isfile, basename
from d2mp import STEAM_EXE, DOTA_EXE, log
import os, re
from shutil import rmtree, copytree


def ensure_exist(func):
    def wrapper(*args, **kw):
        res = func(*args, **kw)
        if not exists(res): os.makedirs(res)
        return res
    return wrapper

def get_file_content(file_path):
    if not isfile(file_path): return None
    return open(file_path).read()

def write_to_file(file_path, content):
    f = open(file_path, "w")
    error = None
    try:
        f.write(content)
    except Exception as e:
        error = e
    finally:
        f.close()
    
    if error is not None: raise error
    

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
    
    @ensure_exist
    def _mod_path(self):
        return join(self._addons_path(), "d2moddin")
    
    @ensure_exist    
    def _d2mp_path(self):
        return join(self._dota_path(), normpath("dota/d2moddin"))
    
    @ensure_exist
    def _addons_path(self):
        return join(self._dota_path(), normpath("dota/addons"))

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
        mod_path = join(self._d2mp_path(), mod_name)
        if not exists(mod_path): 
            log.ERROR("wanted to delete not existing mod: %s" %(mod_name))
            return
        log.DEBUG("deleting mod %s" %(mod_name))
        rmtree(mod_path)
    
    def delete_mods(self):
        rmtree(self._d2mp_path())
        rmtree(self._mod_path())
        log.DEBUG("deleted all present mods")
    
    def set_mod(self, mod_name):
        active_mod = self.get_active_mod()
        if not(active_mod is None or active_mod != mod_name): return
        log.DEBUG("Setting active mod to %s." %mod_name);
        
        rmtree(self._mod_path())
        assert exists(self._d2mp_path())
        from_dir = join(self._d2mp_path(), mod_name.split("=")[0])
        to_dir = join(self._mod_path(), mod_name.split("=")[0])
        assert exists(from_dir)

        copytree(from_dir, to_dir)
        
        f = open(self._mod_name_file(), "w")
        f.write(mod_name)
        f.close()
    
    def _extract_mod_version(self, addon_dir):
        
        log.CRITICAL("TODO: extract mod version")
        return "0.0.0"
#         D2MP.cs: 176
#         log.DEBUG("Found mod %s, detecting version..." %(addon_dir))
#         file_path = join(self._d2mp_path(), join(addon_dir, "addoninfo.txt"))
#         if not isfile(file_path): log.DEBUG("no addoninfo file found: %s" %(file_path))
#         info_file = open(file_path, "r")
#         info_file_content = info_file.read()
#         info_file.close()
#         result = re.match("(addonversion)(\s+)(\d+\.)?(\d+\.)?(\d+\.)?(\*|\d+)", info_file_content)
    
    def _mod_names(self):
        if not self._cache.get('mod_names'):
            names = []
            p = self._d2mp_path()
            for addon_dir in [join(p, f) for f in os.listdir(p)]:
                if not isdir(addon_dir): continue
                mod_version = self._extract_mod_version(addon_dir)
                names.append("%s=%s" %(basename(addon_dir), mod_version))
            if not names: log.ERROR("no mods could be found under %s" %(self._d2mp_path()))
            self._cache['mod_names'] = names
        return self._cache['mod_names']
    
    def mod_list_as_string(self):
        mod_names = self._mod_names()
        if mod_names:
            msg = "You currently have the following detected mods installed:\n\n%s" %(", ".join(self._mod_names()))
        else:
            msg = "You currently have no mods installed"
        return msg
    
    def dota_info_file(self):
        return join(self._dota_path(), normpath("dota/gameinfo.txt"))

    def is_modded(self):
        content = get_file_content(self.dota_info_file())
        regex = "(platform\s+Game.+d2moddin)"
        return re.search(regex, content, flags = re.DOTALL) is not None
    
    def _modify_game_info(self, regex, replacement, should_be_modded):

        if not exists(self.dota_info_file()):
            log.ERROR("dota game info not found under: %s" %(self.dota_info_file()))
            return
        
        
        is_modded = self.is_modded()
        if is_modded and not should_be_modded:
            log.WARN("tried to mod already modded dota game info")
            return 
        elif not is_modded and should_be_modded:
            log.WARN("tried to unmod not modded dota game info")
            return 
            
        content = get_file_content(self.dota_info_file())

        if re.search(regex, content, flags=re.DOTALL) is None:
            log.ERROR("regex does not match: %s" %(regex))
            return 
        
        new_content = re.sub(regex, replacement, content, flags=re.DOTALL)
        write_to_file(self.dota_info_file(), new_content)
    
    def mod_game_info(self):
        regex = "(Game\s+platform)(.+?})"
        replacement = "Game        platform\n      Game        |gameinfo_path|addons\\d2moddin\n    }"
        return self._modify_game_info(regex, replacement, should_be_modded=False)
        
    def unmod_game_info(self):
        regex = "(platform\s+Game.+d2moddin)"
        return self._modify_game_info(regex, "platform", should_be_modded=True)
