"""
created matt_dumont 
on: 17/09/23
"""
from pathlib import Path
import subprocess
from path_support import google_mount_dir
from base_functions import get_user_from_shortcode, join_character, get_rclone_config


def get_google_id(path):
    path = Path(path)
    path = path.relative_to(google_mount_dir)
    mount_name = path.parts[0]
    path = path.relative_to(mount_name)
    parent_path = path.parent
    file_name = path.name
    rclone_config = get_rclone_config(short_code=mount_name.split(join_character)[0])

    code = ' '.join(['rclone',
                     'lsjson',
                     '--drive-impersonate matt@komanawa.com',  # todo testing, do I need impersonate
                     '--config', str(rclone_config),
                     # todo I need the handling of types here, pull from rclone mount options!
                     '--no-mimetype',
                     '--no-modtime',
                     '--fast-list',
                     f'{mount_name}:{parent_path}',
                     ])

    output = subprocess.run(code, capture_output=True, shell=True)
    assert output.returncode == 0, f'failed to get google id for {path}'
    output = output.stdout.decode()
    output = output.split('\n')
    out_id = []
    out_mtype = []
    for l in output:
        if file_name in l:
            l = l.strip(',{}')
            data = {e.split(':')[0].strip('"'): e.split(':')[1].strip('"') for e in l.split(',') if ':' in e}
            if file_name == data['Name']:
                out_id.append(data['ID'])
                out_mtype.append(data['MimeType'])
    if len(out_id) == 0:
        raise ValueError(f'failed to get google id for {path}')
    elif len(out_id) > 1:
        raise ValueError(f'found more than one match for {path}')
    else:
        return out_id[0], out_mtype[0]


def open_in_google_drive(path):
    """
    opens the parent folder in google drive
    :param path:
    :return:
    """
    path = path.parent
    gid, mtype = get_google_id(path)
    link = f'https://drive.google.com/drive/folders/{gid}'
    # todo open in browser
    raise NotImplementedError


def copy_google_drive_link(path): # todo link depends on mmime type... dig into this!
    # todo https://developers.google.com/drive/api/guides/mime-types
    # todo https://developers.google.com/drive/api/guides/ref-export-formats
    gid = get_google_id(path)
    is_sheet =False # todo
    is_doc = False # todo
    is_slide = False # todo
    if is_sheet:
        raise NotImplementedError
