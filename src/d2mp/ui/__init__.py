from PyQt4.Qt import QObject

from d2mp.ui.windows import PreferencesWindow


class UIManager(object):
    
    _instance = None
    
    class signals(QObject):
        pass
    
    def __new__(cls, clear_cache = False):
        if not cls._instance:
            cls._instance = super(UIManager, cls).__new__(cls)
            cls._instance.signals = UIManager.signals()
            cls._instance._windows = {
                "preferences": PreferencesWindow(),
                }
        if clear_cache:
            cls._instance._cache = {}
        return cls._instance
    
    def __init__(self):
        super(UIManager, self).__init__()
    
    def _open(self, window_name):    
        window = self._windows.get(window_name)
        if window is None: return
        return window.show()
        if not window.isActiveWindow():
            window.show()
            window.raise_()
            window.activateWindow()
        else:
            window.show()
    
    def open_preferences(self):
        self._open("preferences")