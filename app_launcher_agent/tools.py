import os
import subprocess
import psutil
from typing import Optional
import platform

class AppLauncherTool:
    """Tool for launching applications on the system."""
    
    def __init__(self):
        self.system = platform.system()
    
    def is_app_running(self, app_name: str) -> bool:
        """Check if an application is already running."""
        for proc in psutil.process_iter(['name']):
            if app_name.lower() in proc.info['name'].lower():
                return True
        return False
    
    def launch_app(self, app_name: str) -> str:
        """Launch an application on the system."""
        try:
            if self.is_app_running(app_name):
                return f"{app_name} is already running."
            
            if self.system == "Windows":
                # Windows-specific launch logic
                apps = {
                    "notepad": "notepad.exe",
                    "chrome": "chrome.exe",
                    "calculator": "calc.exe",
                    "word": "winword.exe",
                    "excel": "excel.exe",
                    "powerpoint": "powerpnt.exe",
                    "paint": "mspaint.exe",
                    "cmd": "cmd.exe",
                    "explorer": "explorer.exe",
                }
                
                # Try to find the app in our dictionary
                executable = apps.get(app_name.lower())
                
                if executable:
                    try:
                        # Use full path for system apps
                        system_path = os.path.join(os.environ['WINDIR'], 'System32')
                        full_path = os.path.join(system_path, executable)
                        
                        if os.path.exists(full_path):
                            subprocess.Popen(full_path)
                            return f"Successfully launched {app_name}"
                        
                        # Fallback to direct execution if path not found
                        subprocess.Popen(executable, shell=True)
                        return f"Successfully launched {app_name}"
                    except Exception as e:
                        return f"Failed to launch {app_name}: {str(e)}"
                
                # Try direct execution for other apps
                try:
                    subprocess.Popen(f'start "" "{app_name}"', shell=True)
                    return f"Attempted to launch {app_name}"
                except Exception as e:
                    return f"Failed to launch {app_name}: {str(e)}"
            
            elif self.system == "Darwin":  # macOS
                try:
                    subprocess.Popen(["open", "-a", app_name])
                    return f"Successfully launched {app_name}"
                except Exception as e:
                    return f"Failed to launch {app_name}: {str(e)}"
            
            elif self.system == "Linux":
                try:
                    subprocess.Popen([app_name])
                    return f"Successfully launched {app_name}"
                except Exception as e:
                    return f"Failed to launch {app_name}: {str(e)}"
            
            return f"Could not launch {app_name}. Please specify the exact application name."
            
        except Exception as e:
            return f"Error launching {app_name}: {str(e)}"