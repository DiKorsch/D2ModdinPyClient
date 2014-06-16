'''
Created on 01.06.2014

@author: Schleppi
'''

import sys
from time import sleep
sys.path.append("..")
from PyQt4.Qt import QApplication, QSharedMemory, QIcon,\
    QSystemTrayIcon, QMenu, QFileSystemWatcher, QTimer
from d2mp import SETTINGS, resources, log
from d2mp.mods import ModManager, write_to_file
import os
from os.path import abspath, join
from d2mp.connection import ConnectionManager
from d2mp.steam import connect_dota, launch_dota, spectate

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

    def is_running(self):
        return self._running
    
    def exec_(self):
        self._create_tray_icon()
        try:
            self._create_mod_manager()
            self._start_file_watcher()
            self._create_socket()
            
        except Exception as e:
            self.show_message("Critical Error", "%s\nClient will shutdown in 10 seconds" %(str(e)), QSystemTrayIcon.Critical)
            QTimer.singleShot(10 * 1000, self.exit)
        
        return super(SingleApplication, self).exec_()
    def _create_mod_manager(self):
        self.manager = ModManager()
        self.manager.mod_game_info()
        self.manager.signals.message.connect(self.show_message_from_mod_manager)
    
    def _create_socket(self):    
        self.socket = ConnectionManager()
        
        self.manager.signals.contact_server.connect(self.socket.send)
        
        self.socket.message.connect(self.show_message_from_socket)
        self.socket.error.connect(self.show_error_from_socket)
        
#         self.socket.shutdown.connect(self.exit)
#         self.socket.uninstall.connect(self.uninstall)
#         
#         self.socket.install_mod.connect(self.manager.install_mod)
#         self.socket.delete_mod.connect(self.manager.delete_mod)
#         self.socket.set_mod.connect(self.manager.set_mod)
#         
#         self.socket.connect_dota.connect(connect_dota)
#         self.socket.launch_dota.connect(launch_dota)
#         self.socket.spectate.connect(spectate)
    
        
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
#         ModManager().uninstall_d2mp()
        self.exit()
    
    def exit(self):
        # do some cleanup
        return super(SingleApplication, self).exit()
    
    def show_mod_list(self):
        self.show_message("Mod List", ModManager().mod_names_as_string())
    
    def show_message_from_socket(self, message):
        self.show_message("Server message", message)
        
    def show_error_from_socket(self, message):
        self.show_message("Server error", message, QSystemTrayIcon.Critical)
        
    def show_message_from_mod_manager(self, message):
        self.show_message("ModManager message", message)
        
    def show_error_from_mod_manager(self, message):
        self.show_message("ModManager error", message, QSystemTrayIcon.Critical)
        
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

