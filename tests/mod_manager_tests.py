'''
Created on 01.06.2014

@author: Schleppi
'''
import unittest

from d2mp.mod_manager import ModManager
from os import path


class ModManagerTest(unittest.TestCase):


    def test_singleton(self):
        man1 = ModManager()
        man2 = ModManager()
        
        self.assertEqual(man1, man2)
        
    def test_steam_and_dota_should_be_installed(self):
        steam_exe = ModManager().find_steam_exe()
        self.assertIsNotNone(steam_exe, "please install steam")
        self.assertTrue(path.exists(steam_exe), "steam executable does not exist: %s" %(steam_exe))
        self.assertTrue(path.isfile(steam_exe), "steam executable should be a file: %s" %(steam_exe))
        
        dota_exe = ModManager().find_dota_exe()
        self.assertIsNotNone(dota_exe, "please install dota!")
        self.assertTrue(path.exists(dota_exe), "dota executable does not exist: %s" %(dota_exe))
        self.assertTrue(path.isfile(dota_exe), "dota executable should be a file: %s" %(dota_exe))
        
        
        
#     def test_