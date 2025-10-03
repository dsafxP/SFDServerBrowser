import subprocess

# Configuration
APP_FOLDER = "core"

def build_gui():
    """Build gui.pyw with flet pack"""
    print("Building GUI with flet pack...")
    
    subprocess.run([
        "flet", 
        "pack", 
        "gui.pyw", 
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
        f"--add-data={APP_FOLDER}:{APP_FOLDER}",
        "main.py"
    ])


if __name__ == "__main__":
    build_gui()
    build_main()
