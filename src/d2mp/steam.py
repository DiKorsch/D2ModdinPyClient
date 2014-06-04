'''
Created on 01.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QDesktopServices, QUrl
import psutil

def command(cmd):
    return QDesktopServices.openUrl(QUrl("steam://%s" %(cmd)))

def launch_dota():
    return command("run/570")

def get_dota_process():
    for proc in psutil.process_iter():
        name = proc.as_dict(['name'])['name'] or ''
        if "dota" in name.lower(): return proc
    return None

def is_dota_running():
    return get_dota_process() is not None

def kill_dota():
    dota_proc = get_dota_process()
    if dota_proc is not None: dota_proc.kill()
    
def connect_dota(address, port):
    command("connect/%s:%s" %(address, port))


def spectate(address, port):
    kill_dota()
    command("rungameid/570//+connect_hltv %s:%s" %(address, port))
        
