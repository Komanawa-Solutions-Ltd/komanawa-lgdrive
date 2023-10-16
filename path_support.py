"""
Template created by matt_dumont
on: 22/03/22
"""
from pathlib import Path

# todo manage imports carefully

proj_root = Path(__file__).parent  # base of git repo
google_mount_dir = Path.home().joinpath('google_mount_point_test') # todo change to google_mount_point
google_mount_dir.mkdir(exist_ok=True)
google_cache_dir = google_mount_dir.joinpath('.cache')
google_cache_dir.mkdir(exist_ok=True)
tray_app_state_path = google_mount_dir.joinpath('.trayapp_state')
icon_path = proj_root.joinpath('gui/kea_icon.png') # todo update icon