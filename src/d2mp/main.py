'''
Created on 01.06.2014

@author: Schleppi
'''

import sys
from PyQt4.Qt import QApplication, QSharedMemory, QIcon,\
    QSystemTrayIcon, QMenu
from d2mp import SETTINGS, resources, log

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
                raise RuntimeError(
                    self._memory.errorString().toLocal8Bit().data())


    def is_running(self):
        return self._running
    
    def exec_(self):
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
        return super(SingleApplication, self).exec_()
        
    def restart(self):
        pass
    def uninstall(self):
        pass
    def show_mod_list(self):
        pass
    

if __name__ == '__main__':
    app = SingleApplication(sys.argv)  
 
    if app.is_running():
        log.DEBUG("[main] d2mp is already running!")
        exit()
    
    log.DEBUG("[main] ready to close")
    r = app.exec_()  
    log.DEBUG("[main] exiting with status %d" %r)
    
    exit(r)

