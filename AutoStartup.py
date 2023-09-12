from os import getcwd, remove, path
from getpass import getuser
from win32com.client import Dispatch

import details

class AutoStartup:

    applicationName = details.applicationName
    applicationPath = f'{getcwd()}\\'+applicationName
    startupPath = rf'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % getuser()

    def add_to_startup(self, exe_path, app_name, mode):
        shortcut_path = self.startupPath+"\\"+app_name

        if mode == "add":
            if path.exists(shortcut_path):
                print("App is already exists...")
            else:
                shell = Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = exe_path
                shortcut.WorkingDirectory = getcwd()
                shortcut.Save()

        elif mode == "del":
            try:
                remove(shortcut_path)
            except OSError:
                print("App is not exists!")

    def check_startup(self, app_name):
        shortcut_path = self.startupPath + "\\" + app_name
        if path.exists(shortcut_path):
            return True
        else:
            return False

    def SAS(self):
        if self.check_startup(self.applicationName+".lnk"):
            self.add_to_startup(self.applicationPath+".exe", self.applicationName+".lnk", mode="del")
            self.add_to_startup(self.applicationPath+".exe", self.applicationName+".lnk", mode="add")
        else:
            self.add_to_startup(self.applicationPath+".exe", self.applicationName+".lnk", mode="add")

    def DAS(self):
        if self.check_startup(self.applicationName+".lnk"):
            self.add_to_startup(self.applicationPath+".exe", self.applicationName+".lnk", mode="del")

