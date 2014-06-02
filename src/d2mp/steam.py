'''
Created on 01.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QDesktopServices, QUrl

def command(cmd):
    return QDesktopServices.openUrl(QUrl("steam://%s" %(cmd)))

def launch_dota():
    return command("run/570")

def is_dota_running():
    return False

def kill_dota():
    pass

def connect_dota(address, port):
    pass

def spectate(address, port):
    pass

