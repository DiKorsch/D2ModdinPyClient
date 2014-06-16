'''
Created on 01.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QSettings, pyqtSignal, QObject
from os.path import join, exists, normpath, isdir, isfile, basename, expanduser
from d2mp import log
import os, re
from shutil import rmtree, copytree
from urllib import urlopen
from zipfile import ZipFile
from StringIO import StringIO


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

def unzip_from_stream(url, dest_dir):
    ZipFile(StringIO(urlopen(url).read())).extractall(dest_dir)

class Mod(object):
    def __init__(self, name, version):
        self.name = name
        self.version = version
    
    def as_dict(self):
        return self.__dict__

class ModManager(object):
    
    _instance = None
    VERSION = "2.3.1"
    
    
    class signals(QObject):
        contact_server = pyqtSignal(object)
        message = pyqtSignal(str)
    
    def __new__(cls, clear_cache = False):
        if not cls._instance:
            cls._instance = super(ModManager, cls).__new__(cls)
            cls._instance._cache = {}
            cls._instance._create_dirs()
            cls._instance.signals = ModManager.signals()
        if clear_cache:
            cls._instance._cache = {}
        return cls._instance
    
    def __init__(self):
        super(ModManager, self).__init__()
    
    def _create_dirs(self):
        for p in [self._d2mp_path(), self._mod_path()]:
            if not isdir(p): os.makedirs(p)
            
    def _steam_path(self):
        if self._cache.get("steam_path") is None:
            if os.name == "nt":
                self._cache["steam_path"] = str(QSettings("HKEY_CURRENT_USER\\Software\\Valve\\Steam", QSettings.NativeFormat).value("SteamPath", "").toString())
            else:
                self._cache["steam_path"] = expanduser("~/.steam/steam")

        return self._cache.get("steam_path")
    
    def _dota_path(self):
        dota_loc = [self._steam_path(), "SteamApps", "common"]
        for p in ["dota 2", "dota 2 beta"]:
            if exists("/".join(dota_loc + [p])): return "/".join(dota_loc + [p])
        
        log.CRITICAL("No dota2 folder found! Please install it!")
        raise Exception("No dota2 folder found! Please install it!")
        
    @ensure_exist
    def _mod_path(self):
        return join(self._addons_path(), "d2moddin")
    
    @ensure_exist    
    def _d2mp_path(self):
        return join(self._dota_path(), normpath("dota/d2moddin"))
    
    @ensure_exist
    def _addons_path(self):
        return join(self._dota_path(), normpath("dota/addons"))

    def _mod_name_file(self):
        return join(self._mod_path(), "modname.txt")
    
    def get_active_mod(self):
        info_file = self._mod_name_file()
        if not isfile(info_file): return None
        name = open(info_file).read()
        log.DEBUG("Current active mod: %s" %name)
        return name

    def install_mod(self, mod_name, version, url):
        log.INFO("Server requested that we install mod " + mod_name + " from download " + url)

        target_dir = join(self._d2mp_path(), mod_name)
        rmtree(target_dir, True)
        os.mkdir(target_dir)
        unzip_from_stream(url, target_dir)

        log.INFO("Mod installed!")
        self.signals.message.emit("Mod %s successfully installed!" %(mod_name))
        self._update_mod(mod_name, version)
        self.signals.contact_server.emit({"msg": "oninstalled", "Mod": Mod(mod_name, version).as_dict()})
    
#     dont think this is a good way of doing it
#     def uninstall_d2mp(self):
#         pass

    def steam_ids(self):
        if not self._cache.get('steam_ids'):
            content = get_file_content(join(self._steam_path(), "config/config.vdf"))
            self._cache['steam_ids'] = re.findall("\"SteamID\"\s+\"(\\d{17})\"", content)
        
        return self._cache.get('steam_ids', [])
    
    def delete_mod(self, mod_name, version = None):
        mod_path = join(self._d2mp_path(), mod_name)
        if not exists(mod_path): 
            log.ERROR("wanted to delete not existing mod: %s" %(mod_name))
            return
        log.DEBUG("deleting mod %s" %(mod_name))
        rmtree(mod_path)
        self._remove_mod(mod_name, version)
        self.signals.contact_server.emit({"msg": "ondeleted", "Mod": Mod(mod_name, version or "0.0.1").as_dict()})
    
    def delete_mods(self):
        rmtree(self._d2mp_path())
        rmtree(self._mod_path())
        log.DEBUG("deleted all present mods")
        self._cache["mods"] = []
    
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
        
        log.DEBUG("Found mod %s, detecting version..." %(addon_dir))
        file_path = join(self._d2mp_path(), join(addon_dir, "addoninfo.txt"))
        if not isfile(file_path): 
            log.DEBUG("no addoninfo file found: %s" %(file_path))
            return "0.0.0"
        regex = "(addonversion\s+)(\d+\.\d+\.\d+)"
        res = re.search(regex, get_file_content(file_path))
        if res is not None:
            return res.group(2)
        else:
            log.CRITICAL("could not extract version number with regex: %s" %(regex))
            return "0.0.0"
    
    def _update_mod(self, mod_name, version):
        mods = self._cache.get("mods", [])
        for mod in mods:
            if mod.name != mod_name: continue
            if mod.version != version:
                mods.remove(mod)
                break
        mods.append(Mod(mod_name, version))
        self._cache["mods"] = mods
    
    def _remove_mod(self, mod_name, version):
        mods = self._cache.get("mods", [])
        for mod in mods:
            if mod.name == mod_name and (not version or mod.version == version):
                mods.remove(mod)
                return
        
        log.ERROR("mod attemted to delete does not exist: %s v%s!" %(mod_name, version))            
        
    def _mods(self):
        if not self._cache.get('mods'):
            p = self._d2mp_path()
            for addon_dir in [join(p, f) for f in os.listdir(p)]:
                if isdir(addon_dir):
                    self._update_mod(basename(addon_dir), self._extract_mod_version(addon_dir)) 
        return self._cache.get('mods', [])
    
    def mod_names(self):
        return [mod.name for mod in self._mods()]
    
    def mods_as_json(self):
        return [mod.as_dict() for mod in self._mods()]

    def mod_names_as_string(self):
        mod_names = self.mod_names()
        if mod_names:
            msg = "You currently have the following detected mods installed:\n\n%s" %(", ".join(mod_names))
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
        if self.is_modded(): return
        regex = "(Game\s+platform)(.+?})"
        replacement = "Game        platform\n      Game        |gameinfo_path|addons\\d2moddin\n    }"
        return self._modify_game_info(regex, replacement, should_be_modded=False)
        
    def unmod_game_info(self):
        if not self.is_modded(): return
        regex = "(platform\s+Game.+d2moddin)"
        return self._modify_game_info(regex, "platform", should_be_modded=True)