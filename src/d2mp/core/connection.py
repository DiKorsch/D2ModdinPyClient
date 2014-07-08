'''
Created on 04.06.2014

@author: Schleppi
'''
from PyQt4.QtCore import pyqtSignal, QObject
from d2mp.core.mods import ModManager

from time import sleep
from d2mp.utils.xsockets import XSocketsClient
from d2mp.utils import log
from os.path import join
from d2mp.utils.steam import launch_dota, connect_dota, spectate

class ConnectionManager(QObject):
    
    offline = False

    server = "net1.d2modd.in"
    port = 4502
    
    address = "ClientController"
    
    message = pyqtSignal(str)
    error = pyqtSignal(str)

    RECONNECT_TIME = 10                     # seconds
    RECONNECT_TIME_AFTER_MAX_ATTEMPS = 2    # minutes
    MAX_ATTEMPS = 3
    
    def get_server_url(self):
        return "ws://%s:%d/%s" %(ConnectionManager.server, ConnectionManager.port, ConnectionManager.address)
    
    def _new_socket(self):
        soc = XSocketsClient(
            self.get_server_url(), 
            onerror = self.handle_error,
            onopen = self.on_open,
            onclose = self.on_close)
        
        soc.bind("commands", self.handle_command)
        self._commands = {
            "wrong_content":    self._wrong_content,              

            "installmod":       self._command_install_mod,
            "delmod":           self._command_del_mod,
            "setmod":           self._command_set_mod,
            
            "close":            self._command_close,
            "uninstall":        self._command_uninstall,
            "launchdota":       self._command_launch,
            "connectdota":      self._command_connect,
            "connectspectate":  self._command_spectate,
        } 
        return soc


    # Commands
        
    def handle_command(self, content):
        self._commands.get(content.get("msg", "wrong_content"), self._command_not_found)(content)
    
    def _wrong_content(self, content):
        log.CRITICAL("haven't expect the content: %s!" %(content))
    
    def _command_not_found(self, content):
        log.CRITICAL("could not found the right command: %s!" %(content.get("msg")))
    
    def _command_install_mod(self, content):
        url = content["url"]
        mod_name = content["Mod"]["name"]
        version = content["Mod"]["version"]
        self.message.emit("Installing Mod %s v%s" %(mod_name, version))
        ModManager().install_mod(mod_name, version, url)
    
    def _command_del_mod(self, content):
        mod_name = content["Mod"]["name"]
        version = content["Mod"]["version"]
        self.message.emit("Uninstalling Mod %s v%s" %(mod_name, version))
        ModManager().delete_mod(mod_name, version)
    
    def _command_set_mod(self, content):
        ModManager().set_mod(content["Mod"]["name"])
    
    
    def _command_close(self, content):
        self.error.emit("Your client version is wrong!\nPlease install the newest version!")
    
    def _command_uninstall(self, content):
        print content
    
    def _command_launch(self, content):
        launch_dota()
        
    def _command_connect(self, content):
        connect_dota(content["ip"])
        
    def _command_spectate(self, content):
        spectate(content["ip"])
    
    
    
    
    
    
    
    
    
    
    def __init__(self):
        super(ConnectionManager, self).__init__()
        if ConnectionManager.offline: 
            return
        self.ws = self._new_socket()
        self._was_disconnected = False
        self._reconnect_tries = 0
    
    def _reconnect(self):
        sleep(self._time_until_reconnect())
        self.ws = self._new_socket()
        
    
    def handle_error(self, message):
        log.DEBUG(message)
        self.error.emit(str(message))
    
    def _time_until_reconnect(self):
        if self._reconnect_tries < ConnectionManager.MAX_ATTEMPS:
            return ConnectionManager.RECONNECT_TIME
        else:
            return ConnectionManager.RECONNECT_TIME_AFTER_MAX_ATTEMPS * 60

    def _time_until_reconnect_as_str(self):
        if self._reconnect_tries < ConnectionManager.MAX_ATTEMPS:
            return "%d seconds" % ConnectionManager.RECONNECT_TIME
        else:
            return "%d minutes" % ConnectionManager.RECONNECT_TIME_AFTER_MAX_ATTEMPS
    
    def on_close(self, *args):
        if self._was_disconnected:
            self._reconnect_tries += 1
        else:
            self._reconnect_tries = 0

        self.error.emit("Disconnected, attempting to reconnect in %s..." %(self._time_until_reconnect_as_str()))
            
        self._was_disconnected = True
        self._reconnect()
    
    def _init_message(self):
        man = ModManager()
        return {
            "msg": "init",
            "SteamIDs": man.steam_ids(),
            "Mods": man.mods_as_json(),
            "Version": man.get_version(),
        }
    
    def send(self, payload):
        self.ws.send(payload, "data")
    
    def on_open(self, *args):
        if self._was_disconnected:
            self.message.emit("Reconnected!")
        else:
            self.message.emit("Connected and ready to begin installing mods!")
        self._was_disconnected = False
        self.send(self._init_message())

