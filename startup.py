import subprocess
import os
import sys
import shutil

import details

if sys.argv[0].endswith(".py"):
    app_name = details.applicationName + ".exe"
else:
    app_name = sys.argv[0]
target_path = os.path.join(os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'), app_name)
current_path = os.path.abspath(app_name)

def make_startup_copy():
    try:
        shutil.copy2(current_path, target_path)
        return True
    except Exception as e:
        print(f"Failed to copy service: {str(e)}")
        return False

def check_startup_exists():
    """
    Check if the scheduled task exists
    Returns: True if exists, False if not
    """
    cmd = ['schtasks', '/query', '/tn', details.applicationName]
    
    try:
        # Remove check=True and check the return code manually
        result = subprocess.run(cmd, 
                                capture_output=True,
                                text=True,
                                shell=True,
                                timeout=10)
        
        # schtasks returns 0 if task exists, 1 if it doesn't exist
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Task check timed out")
        return False
    except Exception as e:
        print(f"Error checking task: {e}")
        return False

def add_to_startup():
    make_startup_copy()
    cmd = [
        'schtasks', '/create', '/tn', details.applicationName,
        '/tr', f'"{target_path}"',  # Task to run (quoted for spaces)
        '/sc', 'onlogon',        # Run at user login
        '/rl', 'highest',        # Run with highest privileges
        '/it',                   # Run only when user is logged in
        '/f'                     # Force creation
    ]
    
    try:
        subprocess.run(cmd, check=True, 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

def remove_startup():
    cmd = ['schtasks', '/delete', '/tn', details.applicationName, '/f']
    try:
        subprocess.run(cmd, check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW)
        os.remove(target_path)
        return True
    except:
        return False

# Example usage:
if __name__ == "__main__":
    # Check if task exists
    if check_startup_exists():
        print("Startup task exists")
        
        # Remove it
        if remove_startup():
            print("Startup task removed successfully")
        else:
            print("Failed to remove startup task")
    else:
        print("Startup task does not exist")
        
        # Add it
        if add_to_startup():
            print("Startup task added successfully")
        else:
            print("Failed to add startup task")