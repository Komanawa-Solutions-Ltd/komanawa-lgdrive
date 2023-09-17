"""
created matt_dumont 
on: 17/09/23
"""
from pathlib import Path
from project_base import google_mount_dir


def get_google_id(path):
    # todo get the google id of a path
    raise NotImplementedError

def copy_path(path, name_only=False, relative_to_drive=False,
              relative_to_project_folder=False,
              for_system='linux', for_user=None): # todo check
    """
    copy a path from the google drive plain text
    :param path: file path
    :param name_only: bool if true then only the name of the file is copied
    :param relative_to_drive: bool if true then the path is relative to the google drive
    :param relative_to_project_folder: bool if true then the path is relative to the project folder
                                       only one of relative_to_drive and relative_to_project_folder can be true
    :param for_system: 'linux' or 'windows', if 'linux' then the path will be converted to a linux path
                        'windows' then the path will be converted to a windows path
    :param for_user: None or user in KSL core, only used if for_system is 'windows'
                     and relative_to_drive is False
                     copy the path as it should appear for the user (e.g. manage their
                     windows mount point.

    :return:
    """
    assert not (relative_to_drive and relative_to_project_folder), 'can only be relative to one thing'
    path = Path(path)
    if name_only:
        path = path.name
        # todo copy to clipboard

    if relative_to_drive:
        path = path.relative_to(google_mount_dir)

    if relative_to_project_folder: # todo check
        path = path.relative_to(google_mount_dir)
        if any( ['YMULT' in e for e in path.parts]):
            # small project
            path = path.relative_to(path.parents[-3])
        else:
            path = path.relative_to(path.parents[-2])
            # large project

    if for_system =='linux':
        pass
    elif for_system == 'windows':
        # todo swap / for \
        raise NotImplementedError
    else:
        raise ValueError(f'unknown system: {for_system=}')

    if for_user is not None and for_system == 'windows':
        raise NotImplementedError
    else:
        # todo save to clipboard
        raise NotImplementedError


def open_in_google_drive(path):
    raise NotImplementedError

def get_google_drive_link(path):
    raise NotImplementedError