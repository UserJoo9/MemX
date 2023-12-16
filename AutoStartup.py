from os import getcwd, remove, path
from getpass import getuser
from win32com.client import Dispatch
import winreg

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

class RegistryStartup:
    def set_autostart_registry(self, app_name, key_data, autostart: bool = True) -> bool:
        """
        Create/update/delete Windows autostart registry key

        ! Windows ONLY
        ! If the function fails, OSError is raised.

        :param app_name:    A string containing the name of the application name
        :param key_data:    A string that specifies the application path.
        :param autostart:   True - create/update autostart key / False - delete autostart key
        :return:            True - Success / False - Error, app name dont exist
        """

        with winreg.OpenKey(
                key=winreg.HKEY_CURRENT_USER,
                sub_key=r'Software\Microsoft\Windows\CurrentVersion\Run',
                reserved=0,
                access=winreg.KEY_ALL_ACCESS,
        ) as key:
            try:
                if autostart:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, key_data)
                else:
                    winreg.DeleteValue(key, app_name)
            except OSError:
                return False
        return True

    def check_autostart_registry(self, value_name):
        """
        Check Windows autostart registry status

        ! Windows ONLY
        ! If the function fails, OSError is raised.

        :param value_name:  A string containing the name of the application name
        :return: True - Exist / False - Not exist
        """

        with winreg.OpenKey(
                key=winreg.HKEY_CURRENT_USER,
                sub_key=r'Software\Microsoft\Windows\CurrentVersion\Run',
                reserved=0,
                access=winreg.KEY_ALL_ACCESS,
        ) as key:
            idx = 0
            while idx < 1_000:  # Max 1.000 values
                try:
                    key_name, _, _ = winreg.EnumValue(key, idx)
                    if key_name == value_name:
                        return True
                    idx += 1
                except OSError:
                    break
        return False
