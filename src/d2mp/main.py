'''
Created on 01.06.2014

@author: Schleppi
'''

import sys
from PyQt4.Qt import QApplication, QSharedMemory, QIcon,\
    QSystemTrayIcon, QMenu, QFileSystemWatcher
from d2mp import SETTINGS, resources, log
from d2mp.mod_manager import ModManager, write_to_file
import os
from os.path import abspath, join
from d2mp.web_socket import WebSocket

class SingleApplication(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        self._memory = QSharedMemory(self)
        self._memory.setKey("d2mp")
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString().toLocal8Bit().data())
        
        self.manager = ModManager()


    def is_running(self):
        return self._running
    
    def exec_(self):
        self._create_tray_icon()
        self.manager.mod_game_info()
        self._start_file_watcher()
        
        self.socket = WebSocket()
        self.socket.message.connect(self.show_message_from_socket)
        self.socket.connect()
        
        return super(SingleApplication, self).exec_()
        
    @property
    def _watcher_file_name(self):
        return "d2mp.pid"
    
    def _start_file_watcher(self):
        self.watcher = QFileSystemWatcher()
        self.watcher_file_path =  join(abspath("."), self._watcher_file_name)
        log.DEBUG("creating watcher file: %s" %(self.watcher_file_path))
        write_to_file(self.watcher_file_path, "Delete this file to shutdown D2MP\n")
        self.watcher.addPath(abspath("."))
        self.watcher.directoryChanged.connect(self._watcher_changed_callback)
    
    def _watcher_changed_callback(self, val):
        if self._watcher_file_name not in os.listdir(val): 
            from time import sleep
            secs = 3
            self.show_message("Shutdown", "Watcher file was deleted. D2MP will shotdown in %d seconds." %(secs))
            sleep(secs)
            self.exit()
    
    def _create_tray_icon(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("D2Moddin Manager")
        self.tray.setIcon(QIcon(SETTINGS['icon']))
        traymenu = QMenu()
        traymenu.addAction("Restart", self.restart)
        traymenu.addAction("Uninstall", self.uninstall)
        traymenu.addAction("Show mod list", self.show_mod_list)
        traymenu.addSeparator()
        traymenu.addAction("Exit", self.exit)
    
        self.tray.setContextMenu(traymenu)
        self.tray.show()
    
    def restart(self):
        python = sys.executable
        args = set(sys.argv)
        args.add("restart")
        os.execl(python, python, *list(sys.argv))
        self.exit()
    
    def uninstall(self):
        ModManager().delete_mods()
        ModManager().uninstall_d2mp()
        self.exit()
    
    def exit(self):
        # do some cleanup
        super(SingleApplication, self).exit()
    
    def show_mod_list(self):
        self.show_message("Mod List", ModManager().mod_list_as_string())
    
    def show_message_from_socket(self, message):
        self.show_message("Server message", message)
    
    def show_message(self, title, message, icon = QSystemTrayIcon.Information):
        self.tray.showMessage(title, message, icon)

if __name__ == '__main__':
    app = SingleApplication(sys.argv)  
 
    if app.is_running():
        log.DEBUG("[main] d2mp is already running!")
        exit()
    
    log.DEBUG("[main] ready to close")
    r = app.exec_()  
    log.DEBUG("[main] exiting with status %d" %r)
    
    exit(r)

