'''
Created on 04.06.2014

@author: Schleppi
'''
from PyQt4.Qt import pyqtSignal, QObject, QTimer
from d2mp.mod_manager import ModManager
import json, thread

from websocket import WebSocketApp

class WebSocket(QObject):

    server = "echo.websocket.org"#"ddp2.d2modd.in"
    port = 80#4502
    
    address = ""#"ClientController"
    
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
    
    def get_server_url(self):
        return "ws://%s:%d/%s" %(WebSocket.server, WebSocket.port, WebSocket.address)
    
    def _new_socket(self):
        return WebSocketApp(self.get_server_url(),
                  on_open = self.on_open, 
                  on_message = self.handle_message,
                  on_error = self.handle_error,
                  on_close = self.on_close)
        
    
    def __init__(self):
        super(WebSocket, self).__init__()
        
        self.ws = self._new_socket()
        self._was_disconnected = False
        thread.start_new_thread(self._connect, ())
    
    def _connect(self):
        self.ws.run_forever()
        
    def handle_error(self, ws, message):
        self.error.emit(message)
    
    def handle_message(self, ws, message):
        content = json.loads(message)
        print content
        # TODO: parse and execute right methods!
    
    def on_close(self, ws):
        self.error.emit("Disconnected, attempting to reconnect in 3 seconds...")
        self._was_disconnected = True
        self.ws = self._new_socket()
        QTimer.singleShot(3 * 1000, self._connect())
        
    def on_open(self, ws):
        if self._was_disconnected:
            self.message.emit("Reconnected!")
        else:
            self.message.emit("Connected and ready to begin installing mods!")
        self._was_disconnected = False
        man = ModManager()
        args = {
            "SteamIDs": man.steam_ids(),
            "Mods": man.mod_list(),
            "Version": man.VERSION, 
        }
        self.ws.send(json.dumps(args))
        
    
