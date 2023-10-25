"""
created matt_dumont 
on: 17/09/23
"""
from pathlib import Path
import subprocess
import webbrowser
from path_support import google_mount_dir
from base_functions import join_character, get_rclone_config, get_drive_export_format


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
                     f'--drive-export-formats {get_drive_export_format()}',  # ensure constant file names
                     '--config', str(rclone_config),
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


def open_in_google_drive(path, open=True):
    """
    opens the parent folder in google drive
    :param path: path to file or folder
    :return:
    """
    path = Path(path)
    if path.is_dir():
        pass
    else:
        path = path.parent
    gid, mtype = get_google_id(path)
    link = f'https://drive.google.com/drive/folders/{gid}'
    if open:
        webbrowser.open(link, new=0, autoraise=True)
    else:
        return link