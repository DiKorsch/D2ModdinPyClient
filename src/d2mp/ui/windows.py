'''
Created on 16.06.2014

@author: Schleppi
'''
from PyQt4.QtGui import QDialog, QFormLayout, QLayout, QWidget, QVBoxLayout,\
    QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QTextBrowser, QIcon,\
    QFileDialog, QTextEdit
from PyQt4.QtCore import Qt, QFileSystemWatcher
from d2mp import SETTINGS
from d2mp.utils import log
from os.path import abspath, exists
from d2mp.core.settings import Settings, is_dota_path_valid, is_steam_path_valid



class BaseDialog(QDialog):
    myLayout = None
    def __init__(self, parent = None, layoutCls = None, fixed = True):
        super(BaseDialog, self).__init__(parent)
        self.myLayout = (layoutCls or QFormLayout)(self)
        self.setLayout(self.myLayout)
        if fixed: self.myLayout.setSizeConstraint(QLayout.SetFixedSize)

class BaseWindow(QWidget):
    def __init__(self, parent = None, layoutCls = None, fixed = True, flags = Qt.Window):
        super(BaseWindow, self).__init__(parent, flags)
        self.myLayout = (layoutCls or QFormLayout)(self)
        self.setLayout(self.myLayout)
        if fixed: self.myLayout.setSizeConstraint(QLayout.SetFixedSize)


class PreferencesWindow(BaseWindow):
    
    def __init__(self, *args, **kwargs):
        super(PreferencesWindow, self).__init__(layoutCls = QVBoxLayout, *args, **kwargs)
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(SETTINGS['icon']))
        self._add_steam_box()
        self._add_dota_box()
        self._add_additional_prefs()
        self._add_log_box()
        
        self._add_log_watcher()
        Settings().signals.changed.connect(self.update_path)
    
    def _add_log_watcher(self):
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(abspath(log.file_name))
        self.watcher.fileChanged.connect(self.update_log)
    
    def show(self):
        self.update_log(abspath(log.file_name))
        return super(PreferencesWindow, self).show()
    
    def update_path(self, setting_key, new_value):
        if setting_key == "dota_path":
            self.dota_path.setText(new_value)
        elif setting_key == "steam_path":
            self.steam_path.setText(new_value)
    
    def _add_steam_box(self):
        box = QGroupBox("Steam Location")
        box.setLayout(QHBoxLayout(box))
        
        self.steam_path = QLineEdit(box)
        self.steam_path.setReadOnly(True)
        self.steam_path.setText(Settings().get("steam_path"))

        change_btn = QPushButton("Change...", box)
        change_btn.clicked.connect(self.change_steam_path)
                
        box.layout().addWidget(self.steam_path)
        box.layout().addWidget(change_btn)
        
        self.layout().addWidget(box)
    
    def _add_dota_box(self):
        box = QGroupBox("Dota Location")
        box.setLayout(QHBoxLayout(box))
        
        self.dota_path = QLineEdit(box)
        self.dota_path.setReadOnly(True)
        self.dota_path.setText(Settings().get("dota_path"))
        
        change_btn = QPushButton("Change...", box)
        change_btn.clicked.connect(self.change_dota_path)

        box.layout().addWidget(self.dota_path)
        box.layout().addWidget(change_btn)
        
        self.layout().addWidget(box)
    
    def change_steam_path(self):
        self._change_path("steam_path", is_steam_path_valid)

    def change_dota_path(self):
        self._change_path("dota_path", is_dota_path_valid)
    
    def _change_path(self, path_key, is_valid):
        new_folder = str(QFileDialog.getExistingDirectory(parent=self, caption="Select new path", directory=Settings().get(path_key)) )
        if new_folder and exists(new_folder):
            if is_valid(new_folder):
                Settings().set(path_key, new_folder)
            else:
                from d2mp.ui import Message
                Message.critical("Path is not valid", 
                            "Path was not saved in settings.\nPlease select a directory with the right executable in it!")
    
    def _add_additional_prefs(self):
        box = QGroupBox("Additional Preferences")
        box.setLayout(QHBoxLayout(box))
                
        log_btn = QPushButton("View Log", box)
        log_btn.clicked.connect(self.open_log_file)
        reset_btn = QPushButton("Reset Settings", box)
        reset_btn.clicked.connect(Settings().reset)
                
        box.layout().addWidget(log_btn)
        box.layout().addWidget(reset_btn)
        
        self.layout().addWidget(box)
        
    def _add_log_box(self):
        box = QGroupBox("Application log")
        box.setLayout(QHBoxLayout(box))
        
        self.log_area = QTextBrowser(box)
        self.log_area.setLineWrapMode(QTextEdit.NoWrap)
        
        box.layout().addWidget(self.log_area)
        self.layout().addWidget(box)
    
    def open_log_file(self):
        log.INFO("TODO: open file in standard editor")
        print abspath(log.file_name)
    
    def update_log(self, log_file):
        content = ""
        for line in open(log_file):
            if "========= new programm start =========" in line:
                content = ""
            else:
                content += line[37:]
        if content:
            self.log_area.setText(content)
        
    
    