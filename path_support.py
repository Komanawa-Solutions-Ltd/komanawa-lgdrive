"""
Template created by matt_dumont
on: 22/03/22
"""
from pathlib import Path

proj_root = Path(__file__).parent  # base of git repo
google_mount_dir = Path.home().joinpath('google_mount_point_test')  # todo change to google_mount_point
google_mount_dir.mkdir(exist_ok=True)
google_cache_dir = google_mount_dir.joinpath('.cache')
google_cache_dir.mkdir(exist_ok=True)

# configs:
base_configs = google_mount_dir.joinpath('.configs')
base_configs.mkdir(exist_ok=True)
master_config = base_configs.joinpath('.master_config')
short_code_path = base_configs.joinpath('.short_codes')
mount_options_path = base_configs.joinpath('.mount_options')
icon_path = proj_root.joinpath('gui/logo2.png')
mounted_drives_path = base_configs.joinpath('.mounted_drives')
google_client_path = base_configs.joinpath('.google_client')
