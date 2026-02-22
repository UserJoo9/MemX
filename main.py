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
import webbrowser
from tkinter import messagebox
import ast

import details
import DataStoring as DS

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class MemX:
    memory_percent = None
    loop = True

    def __init__(self):
        self.gui = Gui(self.start_clean)
        threading.Thread(target=self.percent_cleanup, daemon=True).start()
        threading.Thread(target=self.timing_cleanup, daemon=True).start()

    def start_clean(self):
        if not is_admin():
            messagebox.showwarning("Privilege issue!", "Must be run as Admin!")
            return
        subprocess.call([details.CleanerFileName, details.CleanupKeyword], shell=True)

    def monitor_system(self):
        def monitor():
            while 1:
                try:
                    memory = psutil.virtual_memory()
                    total_memory = str(memory.total / (1024 ** 3))[:5] + " GB"
                    used_memory = str(memory.used / (1024 ** 3))[:5] + " GB"
                    self.memory_percent = memory.percent
                    
                    self.gui.memory_total.configure(text=f"{total_memory}")
                    self.gui.memory_used.configure(text=f"{used_memory}")
                    self.gui.memory_percent_label.configure(text=f"{int(self.memory_percent)}%")
                    
                    # Update progress bar with color transition
                    self.gui.update_progress_bar(self.memory_percent)
                    
                    self.gui.update()
                    time.sleep(1)
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
            time.sleep(0.5)
            while self.loop:
                time.sleep(0.5)
                if self.gui.auto_percent_cleanup_checkbox.get():
                    if int(self.memory_percent) >= int(self.gui.auto_percent_cleanup_entry.get().replace(" %", "")):
                        if self.gui.show_notification.get():
                            self.gui.notification(details.applicationName, f"RAM reached {int(self.memory_percent)}%\n"
                                                                f"{details.applicationName} is cleaning up memory.",
                                                                "OK")
                        self.start_clean()
                        threading.Thread(target=self.continues_loop, daemon=True).start()

    def timing_cleanup(self):
        while 1:
            time.sleep(0.5)
            while self.loop:
                time.sleep(0.5)
                if self.gui.auto_timing_cleanup_checkbox.get():
                    time_out = float(float(self.gui.auto_timing_cleanup_entry.get().split(" ")[0]) * 60)
                    time.sleep(time_out)
                    if self.gui.show_notification.get():
                        self.gui.notification(details.applicationName, f"{details.applicationName} is cleaning up memory\n"
                                                            f"after {time_out} secondes.",
                                                            "OK")
                    self.start_clean()
                    threading.Thread(target=self.continues_loop, daemon=True).start()


class Gui(ctk.CTk):
    def __init__(self, start_clean, **kwargs):
        self.start_clean = start_clean
        super().__init__(**kwargs)

        self.notifications = True

        # Modern dark theme colors
        ctk.set_appearance_mode("dark")
        self.bg_dark = "#0a0e17"
        self.card_bg = "#131821"
        self.accent_primary = "#00ff88"
        self.accent_secondary = "#00d4ff"
        self.text_primary = "#ffffff"
        self.text_secondary = "#8b92a8"
        
        self.title(details.applicationName)
        self.configure(fg_color=self.bg_dark)

        self.SystemTray = Icon(details.applicationName, Image.open(details.imgsPath + "memx.png"), menu=Menu(
            MenuItem(f"Show {details.applicationName}", self.pystrayfunctions),
            MenuItem(f"Exit {details.applicationName}", self.pystrayfunctions)
        ))
        threading.Thread(target=self.SystemTray.run, daemon=True).start()

        self.minsize(340, 410)
        self.resizable(False, False)
        self.iconbitmap(details.imgsPath + "memx.ico")
        self.attributes('-alpha', 0.95)

        # Main container
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.bg_dark)
        self.main_frame.pack(fill="both", expand=True)
        
        # Header with gradient effect simulation
        self.header_frame = ctk.CTkFrame(self.main_frame, corner_radius=0, fg_color=self.card_bg, height=40)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        header_title = ctk.CTkLabel(self.header_frame, text=details.applicationName, 
                                     font=("SF Pro", 24, "bold"),
                                     text_color=self.accent_primary)
        header_title.pack(pady=10)
        
        # Memory stats card with modern design
        self.stats_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.card_bg,
                                       border_width=1, border_color="#1a1f2e")
        self.stats_card.pack(padx=5, pady=(8, 8), fill="x")
        
        # Memory usage display
        stats_inner = ctk.CTkFrame(self.stats_card, corner_radius=12, fg_color="transparent")
        stats_inner.pack(padx=12, pady=5, fill="both")
        
        # Current usage section
        usage_container = ctk.CTkFrame(stats_inner, corner_radius=0, fg_color="transparent")
        usage_container.pack(fill="x", pady=(0, 5))
        
        usage_values = ctk.CTkFrame(usage_container, corner_radius=0, fg_color="transparent")
        usage_values.pack(fill="x", pady=(3, 0))
        
        self.memory_used = ctk.CTkLabel(usage_values, text="0.00 GB", 
                                        font=("SF Pro", 20, "bold"),
                                        text_color=self.text_primary)
        self.memory_used.pack(side="left")
        
        self.memory_percent_label = ctk.CTkLabel(usage_values, text="0%", 
                                                 font=("SF Pro", 16, "bold"),
                                                 text_color=self.accent_primary)
        self.memory_percent_label.pack(side="left", padx=(6, 0))
        
        # Progress bar with modern style
        self.progress_container = ctk.CTkFrame(stats_inner, corner_radius=6, 
                                               fg_color="#0d1117", height=6)
        self.progress_container.pack(fill="x", pady=6)
        self.progress_container.pack_propagate(False)
        
        self.progress_bar = ctk.CTkFrame(self.progress_container, corner_radius=4, 
                                         fg_color=self.accent_primary, width=0)
        self.progress_bar.place(x=1, y=1, relheight=0.65)
        
        # Total memory
        total_container = ctk.CTkFrame(stats_inner, corner_radius=0, fg_color="transparent")
        total_container.pack(fill="x")
        
        ctk.CTkLabel(total_container, text="TOTAL", 
                     font=("SF Pro", 8, "bold"),
                     text_color=self.text_secondary).pack(side="left")
        
        self.memory_total = ctk.CTkLabel(total_container, text="0.00 GB", 
                                        font=("SF Pro", 10, "bold"),
                                        text_color=self.text_primary)
        self.memory_total.pack(side="right")
        
        # Automation controls card
        self.controls_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.card_bg,
                                         border_width=1, border_color="#1a1f2e")
        self.controls_card.pack(padx=5, pady=(0, 8), fill="x")
        
        controls_inner = ctk.CTkFrame(self.controls_card, corner_radius=0, fg_color="transparent")
        controls_inner.pack(padx=5, pady=5, fill="both")
        
        # Time-based cleanup
        time_frame = ctk.CTkFrame(controls_inner, corner_radius=8, fg_color="#0d1117")
        time_frame.pack(fill="x", pady=(0, 6))
        
        time_inner = ctk.CTkFrame(time_frame, corner_radius=0, fg_color="transparent")
        time_inner.pack(padx=5, fill="x")
        
        time_left = ctk.CTkFrame(time_inner, corner_radius=0, fg_color="transparent")
        time_left.pack(side="left", fill="x", pady=2, expand=True)
        
        ctk.CTkLabel(time_left, text="Clean Every", 
                     font=("SF Pro", 9),
                     text_color=self.text_secondary).pack(anchor="w")
        
        self.auto_timing_cleanup_entry = ctk.CTkOptionMenu(
            time_left, 
            values=["5 m", "10 m", "15 m", "20 m", "30 m", "40 m", "45 m", "60 m"],
            font=("SF Pro", 12, "bold"),
            width=75,
            height=24,
            corner_radius=6,
            fg_color="#1a1f2e",
            button_color=self.accent_primary,
            button_hover_color="#00cc70",
            dropdown_fg_color="#1a1f2e",
            dropdown_hover_color="#252b3d"
        )
        self.auto_timing_cleanup_entry.pack(anchor="w", pady=5)
        
        self.auto_timing_cleanup_checkbox = ctk.CTkSwitch(
            time_inner, 
            text="", 
            width=40,
            command=lambda: start_clean(),
            progress_color=self.accent_primary,
            button_color="#1a1f2e",
            button_hover_color="#252b3d"
        )
        self.auto_timing_cleanup_checkbox.pack(side="right")
        
        # Percent-based cleanup
        percent_frame = ctk.CTkFrame(controls_inner, corner_radius=8, fg_color="#0d1117")
        percent_frame.pack(fill="x")
        
        percent_inner = ctk.CTkFrame(percent_frame, corner_radius=0, fg_color="transparent")
        percent_inner.pack(padx=5, fill="x")
        
        percent_left = ctk.CTkFrame(percent_inner, corner_radius=0, fg_color="transparent")
        percent_left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(percent_left, text="Clean at Threshold",
                     font=("SF Pro", 9),
                     text_color=self.text_secondary).pack(anchor="w", pady=2)
        
        self.auto_percent_cleanup_entry = ctk.CTkOptionMenu(
            percent_left,
            values=["10 %","20 %", "30 %", "40 %", "50 %", "60 %", "70 %", "80 %", "90 %", "100 %"],
            font=("SF Pro", 12, "bold"),
            width=75,
            height=24,
            corner_radius=6,
            fg_color="#1a1f2e",
            button_color=self.accent_primary,
            button_hover_color="#00cc70",
            dropdown_fg_color="#1a1f2e",
            dropdown_hover_color="#252b3d"
        )
        self.auto_percent_cleanup_entry.pack(anchor="w", pady=5)
        
        self.auto_percent_cleanup_checkbox = ctk.CTkSwitch(
            percent_inner,
            text="",
            width=40,
            command=lambda: start_clean(),
            progress_color=self.accent_primary,
            button_color="#1a1f2e",
            button_hover_color="#252b3d"
        )
        self.auto_percent_cleanup_checkbox.pack(side="right")
        
        # Action button with glow effect simulation
        button_container = ctk.CTkFrame(self.main_frame, corner_radius=0, fg_color="transparent")
        button_container.pack(padx=5, pady=(4, 8), fill="x")
        
        self.start_button = ctk.CTkButton(
            button_container,
            text="⚡ CLEAN NOW",
            corner_radius=10,
            height=38,
            font=("SF Pro", 13, "bold"),
            command=start_clean,
            fg_color=self.accent_primary,
            hover_color="#00cc70",
            text_color="#0a0e17"
        )
        self.start_button.pack(fill="x")
        
        # Bottom controls
        bottom_frame = ctk.CTkFrame(self.main_frame, corner_radius=0, fg_color="transparent", height=32)
        bottom_frame.pack(fill="x", padx=5, pady=(0, 8))
        bottom_frame.pack_propagate(False)
        
        self.show_notification = ctk.CTkCheckBox(
            bottom_frame,
            text='Notify',
            font=("SF Pro", 12),
            fg_color=self.accent_primary,
            hover_color="#00cc70",
            border_color="#252b3d",
            text_color=self.text_secondary,
            corner_radius=15,
            border_width=1,
            checkbox_width=20,
            checkbox_height=20,
            width=70,
            command=self.control_notifications
        )
        self.show_notification.pack(side="right", pady=6)
        
        infoIcon = Image.open(details.imgsPath + "information.png")
        self.info_button = ctk.CTkButton(
            bottom_frame,
            text='About',
            image=ctk.CTkImage(light_image=infoIcon, dark_image=infoIcon, size=(20, 20)),
            fg_color="transparent",
            hover_color="#1a1f2e",
            text_color=self.text_secondary,
            command=lambda: webbrowser.open_new_tab(details.discord_server),
            width=60,
            height=30,
            corner_radius=6,
            font=("SF Pro", 12)
        )
        self.info_button.pack(side="left", pady=6)

        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())
        x_cordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        self.geometry("{}x{}+{}+{}".format(self.winfo_width(), self.winfo_height(), x_cordinate, y_cordinate - 50))

        if DS.check_registry_value(DS.key_name):
            data = DS.read_from_registry(DS.key_name)
            data = ast.literal_eval(data)
            self.auto_percent_cleanup_entry.set(data["percent"])
            if data['enable_percent']:
                self.auto_percent_cleanup_checkbox.select()
            self.auto_timing_cleanup_entry.set(data["period"])
            if data['enable_period']:
                self.auto_timing_cleanup_checkbox.select()
            if data["notifications"]:
                self.show_notification.select()

    def update_progress_bar(self, percent):
        """Update progress bar with smooth color transition"""
        container_width = self.progress_container.winfo_width()
        if container_width > 0:
            bar_width = int((container_width - 4) * (percent / 100))
            self.progress_bar.configure(width=bar_width)
            
            # Color transition based on percentage
            if percent < 50:
                color = self.accent_primary  # Green
            elif percent < 75:
                color = "#ffd700"  # Yellow
            else:
                color = "#ff4757"  # Red
            
            self.progress_bar.configure(fg_color=color)
            self.memory_percent_label.configure(text_color=color)
        self.save_config()

    def pystrayfunctions(self, icon, event):
        if "Show" in str(event):
            self.deiconify()
        elif "Exit" in str(event):
            self.SystemTray.icon = False
            self.SystemTray.stop()
            self.destroy()

    def notification(self, title, msg, buttonLabel):
        toaster = Notification(
            icon=os.path.abspath(details.imgsPath + "memx.png"),
            app_id=details.applicationName,
            title=title,
            msg=msg,
            duration="short",
        )
        toaster.set_audio(audio.Default, loop=False)
        toaster.add_actions(label=buttonLabel)
        toaster.show()
    
    def save_config(self):
        save_data = {
            "period": self.auto_timing_cleanup_entry.get(),
            "enable_period": self.auto_timing_cleanup_checkbox.get(),
            "percent": self.auto_percent_cleanup_entry.get(),
            "enable_percent": self.auto_percent_cleanup_checkbox.get(),
            "notifications": self.notifications
        }
        DS.write_to_registry(DS.key_name, str(save_data))

    def control_notifications(self):
        if self.show_notification.get():
            self.notifications = True
        else:
            self.notifications = False

if __name__ == "__main__":
    MemX().monitor_system()