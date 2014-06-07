'''
Created on 04.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QTcpSocket, pyqtSignal, QObject
from d2mp.mod_manager import ModManager
import json

# from websocket import WebSocketApp

class WebSocket(QObject):

    server = "ddp2.d2modd.in"
    port = 4502
    
    address = "/ClientController"
    
    message = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self):
        super(WebSocket, self).__init__()
        self.socket = QTcpSocket()
        
        self.socket.connected.connect(self.connected)
        self.socket.disconnected.connect(self.disconnected)
        self.socket.readyRead.connect(self.readyRead)
        self.socket.error.connect(self.handleError)
        
#         self.connect()
    
    def disconnect(self):        
        self.socket.disconnectFromHost()
        if not self.socket.waitForDisconnected(msecs=10000):
            self.message.emit("Can't disconnect from the lobby server!")
            
    def connect(self):        
        self.socket.connectToHost(WebSocket.server, WebSocket.port)
        if not self.socket.waitForConnected(msecs = 10000):
            self.message.emit("Can't connect to the lobby server!")
    
    def handleError(self, socket_error):
        print socket_error, self.socket.errorString()
        
    def readyRead(self):
        print "im ready to read"
    
    def write(self, content):
#         self.socket.write(len(content))
        self.socket.write(content)
        if not self.socket.waitForBytesWritten(msecs=3000):
            self.message.emit("Can't communicate with the lobby server!")
        print "%s is written successfully" %(content)
    
    
    
    def connected(self):
        self.message.emit("Connected and ready to begin installing mods!")
        man = ModManager()
        args = {
            "SteamIDs": man.steam_ids(),
            "Mods": man.mod_list(),
            "Version": man.VERSION, 
        }
        self.write(json.dumps(args))
        
    def disconnected(self):
        self.message.emit("Disconnected, attempting to reconnect...")
        self.connect()
    
        print "i have disconnected"