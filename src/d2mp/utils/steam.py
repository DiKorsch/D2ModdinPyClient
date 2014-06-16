'''
Created on 01.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QDesktopServices, QUrl
import psutil
from d2mp.utils import log

def command(cmd):
    return QDesktopServices.openUrl(QUrl("steam://%s" %(cmd)))

def launch_dota():
    if is_dota_running(): return
    log.DEBUG("Launching dota")
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
    
def connect_dota(ip):
    log.DEBUG("Told Steam to connect to %s." %(ip))
    command("connect/%s" %(ip))


def spectate(ip):
    kill_dota()
    log.DEBUG("Told Steam to spectate at %s." %(ip))
    command("rungameid/570//+connect_hltv %s" %(ip))
        
