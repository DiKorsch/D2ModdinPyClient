'''
Created on 16.06.2014

@author: Schleppi
'''
from PyQt4.Qt import QDialog, QFormLayout, QLayout, QWidget, Qt, QVBoxLayout,\
    QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QTextBrowser, QIcon
from d2mp import SETTINGS


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
    
    def _add_steam_box(self):
        box = QGroupBox("Steam Location")
        box.setLayout(QHBoxLayout(box))
        
        line_edit = QLineEdit(box)
        line_edit.setEnabled(False)
        
        box.layout().addWidget(line_edit)
        box.layout().addWidget(QPushButton("Change...", box))
        
        self.layout().addWidget(box)
    
    def _add_dota_box(self):
        box = QGroupBox("Dota Location")
        box.setLayout(QHBoxLayout(box))
        
        line_edit = QLineEdit(box)
        line_edit.setEnabled(False)
        
        box.layout().addWidget(line_edit)
        box.layout().addWidget(QPushButton("Change...", box))
        
        self.layout().addWidget(box)
    
    def _add_additional_prefs(self):
        box = QGroupBox("Additional Preferences")
        box.setLayout(QHBoxLayout(box))
                
        log_btn = QPushButton("View Log", box)
        reset_btn = QPushButton("Reset Settings", box)
                
        box.layout().addWidget(log_btn)
        box.layout().addWidget(reset_btn)
        
        self.layout().addWidget(box)
        
    def _add_log_box(self):
        box = QGroupBox("Application log")
        box.setLayout(QHBoxLayout(box))
        
        text_area = QTextBrowser(box)
        
        box.layout().addWidget(text_area)
        self.layout().addWidget(box)
        
        
    
    