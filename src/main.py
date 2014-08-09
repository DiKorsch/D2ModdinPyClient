'''
Created on 01.06.2014

@author: Schleppi
'''
import sys
sys.path.append(".")

from time import sleep
from d2mp.ui import UIManager
from d2mp.core.settings import Settings
from d2mp import resources
from PyQt4.QtCore import QSharedMemory, QFileSystemWatcher, QTimer,\
    QCoreApplication
from PyQt4.QtGui import QApplication, QIcon, QSystemTrayIcon, QMenu
from d2mp import SETTINGS
from d2mp.utils import log
from d2mp.core.mods import ModManager, write_to_file
import os
from os.path import abspath, join
from d2mp.core.connection import ConnectionManager


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
        self._create_mod_manager()
        self._start_file_watcher()
        self._create_socket()
        Settings()
        
        return super(SingleApplication, self).exec_()
    def _create_mod_manager(self):
        self.manager = ModManager()
        self.manager.mod_game_info()
        self.manager.signals.message.connect(self.show_message_from_mod_manager)
        self.manager.signals.error.connect(self.show_error_from_mod_manager)
    
    def _create_socket(self):    
        self.socket = ConnectionManager()
        
        self.manager.signals.contact_server.connect(self.socket.send)
        
        self.socket.message.connect(self.show_message_from_socket)
        self.socket.error.connect(self.show_error_from_socket)
        
        
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
        traymenu.addAction("Preferences", UIManager().open_preferences)
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
    app.setQuitOnLastWindowClosed(False);

    if app.is_running():
        log.DEBUG("[main] d2mp is already running!")
    else:
        QCoreApplication.setOrganizationName("D2Modd");
        QCoreApplication.setOrganizationDomain("d2modd.in");
        QCoreApplication.setApplicationName("D2ModdInClient");
        
        log.DEBUG("[main] ready to close")
        r = app.exec_()  
        log.DEBUG("[main] exiting with status %d" %r)
    

