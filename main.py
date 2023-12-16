import customtkinter as ctk
import subprocess
import psutil
import time
import threading
from pystray import Menu, MenuItem, Icon
from PIL import Image
from winotify import Notification, audio
import os
import ctypes
import ctypes.wintypes
import webbrowser
from CTkToolTip import CTkToolTip
import sys

import details
import AutoStartup


class MemX:

    memory_percent = None
    loop = True

    def __init__(self, argv):
        self.auto_startup = AutoStartup.RegistryStartup()
        if not self.auto_startup.check_autostart_registry(details.applicationName):
            self.auto_startup.set_autostart_registry(details.applicationName, f'"{os.path.abspath(sys.argv[0])}"' + ' -hide', autostart=False)
            self.auto_startup.set_autostart_registry(details.applicationName, f'"{os.path.abspath(sys.argv[0])}"' + ' -hide')
        self.gui = Gui(self.start_clean)
        if argv == '-hide':
            self.gui.withdraw()
        threading.Thread(target=self.percent_cleanup, daemon=True).start()
        threading.Thread(target=self.timing_cleanup, daemon=True).start()

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def get_admin(self):
        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            self.gui.pystrayfunctions(None, "Exit")

    def start_clean(self, check=False):
        if not check:
            if self.is_admin():
                subprocess.call([details.CleanerFileName, details.CleanupKeyword], shell=True)
            else:
                self.get_admin()
        else:
            self.get_admin()

    def monitor_system(self):
        def monitor():
            while 1:
                try:
                    memory = psutil.virtual_memory()
                    total_memory = str(memory.total / (1024 ** 3))[:5] + " GB"
                    used_memory = str(memory.used / (1024 ** 3))[:5] + " GB"
                    self.memory_percent = memory.percent
                    self.gui.memory_total.configure(text=f"Total memory: {total_memory}")
                    self.gui.memory_used.configure(text=f"Current Usage: {used_memory} ({int(self.memory_percent)}%)")
                    self.gui.update()
                    time.sleep(0.5)
                except:
                    pass
        threading.Thread(target=monitor, daemon=True).start()
        self.gui.mainloop()

    def continues_loop(self):
        self.loop = False
        time.sleep(5)
        self.loop = True


    def percent_cleanup(self):
        while 1:
            time.sleep(0.1)
            while self.loop:
                time.sleep(0.1)
                if self.gui.auto_percent_cleanup_checkbox.get():
                    if int(self.memory_percent) >= int(self.gui.auto_percent_cleanup_entry.get().replace(" %", "")):
                        self.gui.notification(details.applicationName, f"RAM reached {int(self.memory_percent)}%\n"
                                                               f"{details.applicationName} is cleaning up memory.",
                                                               "OK")
                        self.start_clean()
                        threading.Thread(target=self.continues_loop, daemon=True).start()

    def timing_cleanup(self):
        while 1:
            time.sleep(0.1)
            while self.loop:
                time.sleep(0.1)
                if self.gui.auto_timing_cleanup_checkbox.get():
                    time_out = float(float(self.gui.auto_timing_cleanup_entry.get().split(" ")[0]) * 60)
                    time.sleep(time_out)
                    self.gui.notification(details.applicationName, f"{details.applicationName} is cleaning up memory\n"
                                                           f"after {time_out} minutes.",
                                                           "OK")
                    self.start_clean()
                    threading.Thread(target=self.continues_loop, daemon=True).start()

class Gui(ctk.CTk):

    auto_startup = AutoStartup.AutoStartup()

    def __init__(self, start_clean, **kwargs):
        self.start_clean = start_clean
        super().__init__(**kwargs)
        self.title(details.applicationName)

        self.SystemTray = Icon(details.applicationName, Image.open(details.png_icon), menu=Menu(
            MenuItem(f"{details.applicationName} Clean", self.pystrayfunctions),
            MenuItem(f"Show {details.applicationName}", self.pystrayfunctions),
            MenuItem(f"Hide {details.applicationName}", self.pystrayfunctions),
            MenuItem(f"Exit {details.applicationName}", self.pystrayfunctions)
        ))
        threading.Thread(target=self.SystemTray.run, daemon=True).start()

        self.minsize(400, 200)
        self.resizable(False, False)
        self.iconbitmap(details.ico_icon)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand="true")
        self.main_frame.columnconfigure(0, weight=1)

        self.memory_total = ctk.CTkLabel(self.main_frame, text="Total Memory: None", font=("roboto", 20, "bold"))
        self.memory_total.grid(row=1, column=0, columnspan=3, pady=10, padx=20, sticky='w')

        self.memory_used = ctk.CTkLabel(self.main_frame, text="Current Used: None", font=("roboto", 20, "bold"))
        self.memory_used.grid(row=2, column=0, columnspan=3, pady=10, padx=20, sticky='w')

        self.auto_timing_cleanup_label = ctk.CTkLabel(self.main_frame, text="Automatic clean every ", font=("roboto", 20, "bold"))
        self.auto_timing_cleanup_label.grid(row=3, column=0, pady=10, padx=(20, 5), sticky='w')

        self.auto_timing_cleanup_entry = ctk.CTkOptionMenu(self.main_frame, values=["5 m", "10 m", "15 m", "20 m", "30 m", "40 m", "45 m", "60 m"],
                                                  font=("roboto", 20, "bold"), width=100)
        self.auto_timing_cleanup_entry.grid(row=3, column=1, pady=10, sticky='w')

        self.auto_timing_cleanup_checkbox = ctk.CTkCheckBox(self.main_frame, text="", width=50, command=lambda: start_clean(check=True))
        self.auto_timing_cleanup_checkbox.grid(row=3, column=2, pady=10, padx=5, sticky='w')

        self.auto_percent_cleanup_label = ctk.CTkLabel(self.main_frame, text="Clean when RAM reach ", font=("roboto", 20, "bold"))
        self.auto_percent_cleanup_label.grid(row=4, column=0, pady=10, padx=(20, 5), sticky='w')

        self.auto_percent_cleanup_entry = ctk.CTkOptionMenu(self.main_frame, values=["10 %","20 %", "30 %", "40 %", "50 %", "60 %", "70 %", "80 %", "90 %", "100 %"],
                                                    font=("roboto", 20, "bold"), width=100)
        self.auto_percent_cleanup_entry.grid(row=4, column=1, pady=10, sticky='w')

        self.auto_percent_cleanup_checkbox = ctk.CTkCheckBox(self.main_frame, text="", width=50, command=lambda: start_clean(check=True))
        self.auto_percent_cleanup_checkbox.grid(row=4, column=2, pady=10, padx=5, sticky='w')

        self.start_button = ctk.CTkButton(self.main_frame, text="MemX Clean", corner_radius=15, width=150, font=("roboto", 20, "bold"), command=start_clean)
        self.start_button.grid(row=5, column=0, columnspan=3, pady=10, padx=10)
        CTkToolTip(self.start_button, message="Clean memory now")

        infoIcon = Image.open(details.resource_path("information.png"))
        self.info_button = ctk.CTkButton(self.main_frame, text='', image=ctk.CTkImage(light_image=infoIcon, dark_image=infoIcon, size=(25, 25)),
                                         fg_color=self.main_frame.cget("fg_color"), bg_color=self.main_frame.cget("fg_color"),
                                         command=lambda: webbrowser.open("https://www.instagram.com/_youssefelkhodary/"),  width=10, corner_radius=15)
        self.info_button.place(x=5, y=200)
        CTkToolTip(self.info_button, message="Contact developer")

        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())
        x_cordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        self.geometry("{}+{}".format(x_cordinate, y_cordinate - 50))

    def pystrayfunctions(self, icon, event):
        if f"{details.applicationName} Clean" in str(event):
            self.start_clean()
        elif "Show" in str(event):
            self.deiconify()
        elif "Hide" in str(event):
            self.withdraw()
        elif "Exit" in str(event):
            self.SystemTray.icon = False
            self.SystemTray.stop()
            self.destroy()

    def notification(self, title, msg, buttonLabel):
        toaster = Notification(
            icon=os.path.abspath(details.png_icon),
            app_id=details.applicationName,
            title=title,
            msg=msg,
            duration="short",
        )
        toaster.set_audio(audio.Default, loop=False)
        toaster.add_actions(label=buttonLabel)
        toaster.show()


if __name__ == "__main__":
    argv = None
    try:
        argv = sys.argv[1]
    except:
        pass
    MemX(argv=argv).monitor_system()