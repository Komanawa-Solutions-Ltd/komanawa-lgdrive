"""
Template created by matt_dumont
on: 22/03/22
"""
from pathlib import Path
from kslcore import KslEnv

project_name = '' # todo fill out
proj_root = Path(__file__).parent  # base of git repo
project_dir = KslEnv.shared_gdrive.joinpath('{project shared dir}')  # todo fill out the project dir
unbacked_dir = KslEnv.unbacked.joinpath(project_name)
unbacked_dir.mkdir(exist_ok=True)

# todo also consider adding key directories e.g.
# data_dir = project_dir.joinpath("data")
# results_dir = project_dir.joinpath("results")
