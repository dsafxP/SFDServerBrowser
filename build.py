import subprocess

# Configuration
ICON = "img/SFDicon.ico"
APP_FOLDER = "app"

def build_gui():
    """Build gui.pyw with flet pack"""
    print("Building GUI with flet pack...")
    
    subprocess.run([
        "flet", 
        "pack", 
        "gui.pyw", 
        "--icon", 
        ICON, 
        "--name", 
        "SFDServerBrowser_gui"
    ])


def build_main():
    """Build main.py with PyInstaller"""
    print("Building main executable with PyInstaller...")

    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--name=SFDServerBrowser_cli",
        f"--icon={ICON}",
        f"--add-data={APP_FOLDER}:{APP_FOLDER}",
        "main.py"
    ])


if __name__ == "__main__":
    build_gui()
    build_main()