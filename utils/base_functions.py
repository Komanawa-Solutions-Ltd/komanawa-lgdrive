"""
created matt_dumont 
on: 17/09/23
"""
import time
import warnings
import numpy as np
import subprocess
from path_support import google_mount_dir, google_cache_dir, base_configs, short_code_path, mount_options_path, \
    master_config

join_character = '~'
base_tmux_name = f'*gd{join_character}' + '{}' + join_character + '{}'

light_mount_option = (
    '--drive-export-formats link.html',  # manage drive formats so google docs download as .html links
    '--stats=0',  # disables printing of stats
    '--bwlimit=100M',  # up and down limits
    '--vfs-cache-mode full',
    '--vfs-cache-max-age 5h',
)

base_mount_options = (
    '--drive-export-formats link.html',  # manage drive formats so google docs download as .html links
    '--stats=0',  # disables printing of stats
    '--bwlimit=200M',  # up and down limits
    '--vfs-cache-mode full',
    '--vfs-cache-poll-interval 30s',
    '--vfs-cache-max-size 50G',
    '--vfs-read-ahead 500M',
    '--drive-pacer-burst 200',  # Number of API calls to allow without sleeping.
    '--drive-pacer-min-sleep 10ms',  # Minimum time to sleep between API calls.
    '--drive-chunk-size 256M',
    # Upload chunk size. higher = more memory, lower = slower upload, Must a power of 2 >= 256k
    '--drive-upload-cutoff 256M',  # Cutoff for switching to chunked upload.

    # --drive-list-chunk 1000 #  do not understand
    # dir-cache-time Duration (default 5m0s)  # time to re-look for directories... 5m seems about right
    '--vfs-cache-max-age 24h',
)  # Max time since last access of objects in the cache (default 1h0m0s)


def get_prebuilt_mount_options(key):
    poss_keys = ('light', 'default')
    assert key in poss_keys, f'{key=} must be one of {poss_keys}'
    if key == 'light':
        return light_mount_option
    elif key == 'default':
        return base_mount_options
    else:
        raise ValueError("shouldn't get here")


def close_google_drive():
    """ unmount all drives, raise if drives are still mounted"""
    mount_names = list_active_drive_mounts()
    mount_names = [get_mountpoint_tmux_name(*get_email_from_mountpoint_tmux_name(tmux_name=nm),
                                            return_email=False)[1] for nm in mount_names]

    for nm in mount_names:
        if is_mounted(nm):
            unmount_drive(nm)

    for nm in mount_names:
        if is_mounted(nm):
            raise ValueError(f'{nm} is still mounted')
    return True


def get_rclone_config(email_address=None, short_code=None):
    if email_address is None and short_code is None:
        raise ValueError('must provide email_address or short_code')
    elif email_address is not None and short_code is not None:
        raise ValueError('must provide email_address or short_code, not both')
    if short_code is None:
        short_code = get_user_shortcode(email_address)

    config_name = f'.{short_code}.rclone.conf'
    config_path = base_configs.joinpath(config_name)
    if not config_path.exists():
        _create_config(email_address)

    return config_path


def _create_config(email_address, drives):  # todo

    raise NotImplementedError


def authenticate(email_address):  # todo?
    # todo setup My_Drive
    # todo write/update master config... (this is the config that is used to list all avalbile drives),
    #   only
    # https://rclone.org/commands/rclone_authorize/
    raise NotImplementedError


def is_mounted(nm):
    """
    check drive nm is mounted (by looking for tmux env
    :param nm:
    :return:
    """
    mounted = False
    time.sleep(1)
    shortcode, drive_name = get_email_from_mountpoint_tmux_name(mp_name=nm)
    # check if tmux session exists
    tmux_nm, mp_name = get_mountpoint_tmux_name(drive_name, shortcode=shortcode)
    assert mp_name == nm, f'{mp_name=} != {nm=}'
    tmux_nm = base_tmux_name.format(nm)  # these are listed in alphabetical order
    tmuxdirs = subprocess.run('tmux ls', capture_output=True, shell=True).stdout.decode()
    tmuxdirs = tmuxdirs.split('\n')
    tmuxdirs = [e.split(':')[0] for e in tmuxdirs]
    if tmux_nm in tmuxdirs:  # allow skipping.
        mounted = True

    mount_dir = google_mount_dir.joinpath(mp_name)
    # check if drive is mounted in bash
    code = f"mount | grep {mount_dir}"
    output = subprocess.run(code, capture_output=True, shell=True).stdout.decode()
    if output != '':
        mounted = True

    return mounted


def get_mountpoint_tmux_name(drive_name, shortcode=None, email_address=None):
    if shortcode is None and email_address is None:
        raise ValueError('must provide shortcode or email_address')

    if shortcode is None:
        shortcode = get_user_shortcode(email_address)
    assert shortcode is not None
    tmux_nm = base_tmux_name.format(shortcode, drive_name)
    mp_name = join_character.join([shortcode, drive_name])
    return tmux_nm, mp_name


def get_email_from_mountpoint_tmux_name(tmux_name=None, mp_name=None, return_email=False):
    """
    get email address from tmux name or mountpoint name
    :param tmux_name: tmux name, pass either tmux_name or mp_name
    :param mp_name: mount point name, pass either tmux_name or mp_name
    :param return_email: bool if true return email address, else return shortcode
    :return:
    """
    assert tmux_name is not None or mp_name is not None, f'must provide tmux_name or mp_name'
    assert not (tmux_name is not None and mp_name is not None), f'cannot provide both tmux_name and mp_name'
    if tmux_name is not None:
        shortcode, drive_name = tmux_name.split(join_character)[1:]
    elif mp_name is not None:
        shortcode, drive_name = mp_name.split(join_character)
    else:
        raise ValueError('should not get here')

    if return_email:
        return drive_name, get_user_from_shortcode(shortcode)
    else:
        return drive_name, shortcode


def mount_drive(email_address, drive_name):
    """
    mount a google drive in a tmux session
    :param email_address:
    :param drive_name:
    :return:
    """
    options = read_options()
    mp_name, tmux_nm = get_mountpoint_tmux_name(drive_name, shortcode=None, email_address=email_address)
    config_path = get_rclone_config(email_address)
    if is_mounted(drive_name):
        print(f'skipping {drive_name} already mounted')
    else:
        mount_dir = google_mount_dir.joinpath(mp_name)
        mount_dir.mkdir(parents=True, exist_ok=True)
        cache = google_cache_dir.joinpath(mp_name)
        cache.mkdir(exist_ok=True)
        assert mount_dir.is_dir(), f'mount_dir {mount_dir} is not a dir'
        assert len(list(mount_dir.iterdir())) == 0, f'mount_dir {mount_dir} is not empty'

        # create tmux session for the mount then mount the drive.
        code = ' '.join([
            f"tmux new -s {tmux_nm} -d",  # run in tmux
            f'rclone -v --drive-impersonate {email_address}',  # todo is this needed without system token?
            f'--config {config_path}',  # email specific config file
            f'--cache-dir {cache}',  # cache dir
            *options,  # mount options
            f'mount {drive_name}:  {mount_dir}'])
        subprocess.run(code, shell=True)
        success = True
        error = ''
        if not is_mounted(drive_name):
            success = False
            error = f'mount failed for {drive_name}'
        list_paths_mount(tmux_nm)
        return success, error


def list_paths_mount(tmux_name):
    # todo basically prime start mount so that it's not super laggy when first flying
    # todo look into
    # todo lots of folks rc vfs/refresh recursive=true
    raise NotImplementedError


def list_active_drive_mounts():
    """
    list all active drive mounts
    :return: list of tmux dirs
    """
    tmuxdirs = subprocess.run('tmux ls', capture_output=True, shell=True).stdout.decode()
    tmuxdirs = tmuxdirs.split('\n')
    tmuxdirs = [e.split(':')[0] for e in tmuxdirs]
    return tmuxdirs


def user_authenticated(email_address=None, shortcode=None):  # todo
    raise NotImplementedError


def get_user_shortcode(email_address):
    return _read_shortcodes()[email_address]


def add_user_set_shortcode(email_address, shortcode=None):
    # short code to prepend to the mount name (e.g. hm for home users), user defined
    if shortcode is None:
        shortcode = email_address.split('@')[0]
    short_codes = _read_shortcodes()
    inv = {v: k for k, v in short_codes.items()}
    bad_chars = [' ', '\t', '\n', '\r', '/', '\\', '?', '<', '>', '|', ':', '*', '"', "'", '=']
    success = True
    mssage = ''
    if shortcode in short_codes.values():
        success = False
        mssage = f'{shortcode} already in use for {inv[shortcode]}'
    elif any([e in shortcode for e in bad_chars]):
        success = False
        mssage = f'bad characters in {shortcode}, cannot use {bad_chars}'
    elif shortcode[0] == '-':
        success = False
        mssage = f'cannot start with "-"'
    else:
        short_codes[email_address] = shortcode
        _write_shortcodes(short_codes)
    return success, mssage


def get_user_from_shortcode(shortcode):
    t = _read_shortcodes()
    t = {v: k for k, v in t.items()}
    return t[shortcode]


def _read_shortcodes():
    if not short_code_path.exists():
        return {}
    with short_code_path.open('r') as f:
        lines = f.readlines()
    out = {}
    for line in lines:
        line = line.split('=')
        out[line[0]] = line[1]
    return out


def _write_shortcodes(short_codes):
    with short_code_path.open('w') as f:
        for k, v in short_codes.items():
            f.write(f'{k}={v}\n')


def list_drives_available(email_address):
    """
    get possible drives that could be mounted for a given email address
    :param email_address:
    :return: dict of drive names and info
    {drivename(inc short code): {id:###, kind:###, name:###(w/o shortcode), shortcode:###}}
    """
    shortcode = get_user_shortcode(email_address)
    code = ' '.join(['rclone',
                     'backend',
                     'drives',
                     '--config', str(master_config),
                     '--drive-impersonate matt@komanawa.com',  # todo do I need this, likely not
                     f'{shortcode}:'
                     ])
    output = subprocess.run(code, capture_output=True, shell=True)
    assert output.returncode == 0, f'failed to list google drives for {email_address}'
    out = output.stdout.decode()
    outdata = {}
    for line in out.split('\n'):
        if line != '':
            line = line.strip()
            line = line.strip(',{}')
            temp = {}
            for e in line.split(','):
                k = e.split(':')[0].strip('"')
                v = e.split(':')[1].strip('"')
                temp[k] = v
            temp['shortcode'] = shortcode
            outkey = get_mountpoint_tmux_name(temp['name'], shortcode=shortcode)[1]
            outdata[outkey] = temp
    return outdata


def write_options(options):
    with mount_options_path.open('w') as f:
        for line in options:
            f.write(line + '\n')


def read_options():
    with mount_options_path.open('r') as f:
        lines = f.readlines()
    lines = [e.strip('\n') for e in lines]
    return lines


def get_drive_export_format():
    options = read_options()
    for line in options:
        if '--drive-export-formats' in line:
            return line.split(' ')[1]


def _update_master_config(add_email, remove_email):  # todo
    """
    update the master config file to include add_email and remove remove_email
    :param add_email:
    :param remove_email:
    :return:
    """
    raise NotImplementedError


def unmount_drive(nm):
    mount_dir = google_mount_dir.joinpath(nm)
    code = f"umount {mount_dir}"
    output = subprocess.run(code, shell=True)
    return output.returncode == 0
