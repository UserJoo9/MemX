import sys
import os

import os
import sys

def resource_path(relative_path):
    if hasattr(sys, "frozen") or hasattr(sys, "real_path"):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, relative_path)
    
    if not os.path.exists(path):
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f"File not found: {relative_path}", "Error", 0x10)
        sys.exit(1)
        
    return path

applicationName = "MemX"
CleanerFileName = resource_path("EmptyStandbyList.exe")
CleanupKeyword = "workingsets"
imgsPath = resource_path("imgs\\")
discord_server = "https://beacons.ai/youssefalkhodary"