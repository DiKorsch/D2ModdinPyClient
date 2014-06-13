'''
Created on 04.06.2014

@author: Schleppi
'''
from PyQt4.Qt import pyqtSignal, QObject
from d2mp.mod_manager import ModManager
import json, thread

from websocket import WebSocketApp, enableTrace
from time import sleep
from d2mp.xsockets import XSocketsClient
from d2mp import log

# enableTrace(True)

class WebSocket(QObject):
    
    offline = False

    server = "ddp2.d2modd.in"
    port = 4502
    
    address = "ClientController"
    
    message = pyqtSignal(str)
    error = pyqtSignal(str)

    shutdown = pyqtSignal()
    uninstall = pyqtSignal()
    install_mod = pyqtSignal(str, str, str) # mod_name, version, url
    delete_mod = pyqtSignal(str)            # mod_name
    set_mod = pyqtSignal(str)               # mod_name
    connect_dota = pyqtSignal(str, int)     # address, port
    launch_dota = pyqtSignal()
    spectate = pyqtSignal(str, int)         # address, port

    RECONNECT_TIME = 10                     # seconds
    RECONNECT_TIME_AFTER_MAX_ATTEMPS = 2    # minutes
    MAX_ATTEMPS = 1
    
    def get_server_url(self):
        return "ws://%s:%d/%s" %(WebSocket.server, WebSocket.port, WebSocket.address)
    
    def _new_socket(self):
        soc = XSocketsClient(
            self.get_server_url(), 
            onerror = self.handle_error,
            onopen = self.on_open,
            onclose = self.on_close)
        
        soc.bind("commands", self.handle_commands)
        return soc
        
    def handle_commands(self, *args):
        print args
    
    def __init__(self):
        super(WebSocket, self).__init__()
        if WebSocket.offline: 
            print ModManager().mods_as_json()
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
        if self._reconnect_tries < WebSocket.MAX_ATTEMPS:
            return WebSocket.RECONNECT_TIME
        else:
            return WebSocket.RECONNECT_TIME_AFTER_MAX_ATTEMPS * 60

    def _time_until_reconnect_as_str(self):
        if self._reconnect_tries < WebSocket.MAX_ATTEMPS:
            return "%d seconds" % WebSocket.RECONNECT_TIME
        else:
            return "%d minutes" % WebSocket.RECONNECT_TIME_AFTER_MAX_ATTEMPS
    
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
            "Version": man.VERSION, 
        }
    
    def on_open(self, *args):
        if self._was_disconnected:
            self.message.emit("Reconnected!")
        else:
            self.message.emit("Connected and ready to begin installing mods!")
        self._was_disconnected = False
        self.ws.send(self._init_message(), "data")

