"""
created matt_dumont 
on: 9/11/23
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from gui.google_drive_tray_pyqt import launch_panel_app

# todo this is what to call to run the applet
if __name__ == '__main__':
    launch_panel_app()
