"""
created matt_dumont 
on: 17/09/23
"""
import time
import warnings

import numpy as np
import subprocess
from path_support import google_mount_dir, google_cache_dir, base_configs, short_code_path

join_character = '~' # todo does this character cause problems?
base_tmux_name = f'*gd{join_character}'+'{}' + join_character + '{}'


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

    # --drive-list-chunk 1000 # todo do not understand
    # dir-cache-time Duration (default 5m0s)  # time to re-look for directories... 5m seems about right
    '--vfs-cache-max-age 24h',
)  # Max time since last access of objects in the cache (default 1h0m0s)


def close_google_dirve():
    raise NotImplementedError


def restart_google_drive():
    raise NotImplementedError


def get_avalible_shared_drives():
    raise NotImplementedError


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


def _create_config(email_address):
    raise NotImplementedError


def authenticate(email_address):  # todo how?
    raise NotImplementedError


def is_mounted(nm):
    """
    check drive nm is mounted (by looking for tmux env
    :param nm:
    :return:
    """
    mounted = False
    time.sleep(1)
    # check if tmux session exists
    tmux_nm = base_tmux_name.format(nm)  # these are listed in alphabetical order
    tmuxdirs = subprocess.run('tmux ls', capture_output=True, shell=True).stdout.decode()
    tmuxdirs = tmuxdirs.split('\n')
    tmuxdirs = [e.split(':')[0] for e in tmuxdirs]
    if tmux_nm in tmuxdirs:  # allow skipping.
        mounted = True

    # todo check if drive is mounted in bash
    return mounted


def get_mountpoint_tmux_name(email_address, drive_name):
    shortcode = get_user_shortcode(email_address)
    tmux_nm = base_tmux_name.format(shortcode, drive_name)
    mp_name = '~'.join([shortcode, drive_name])  # todo does this character cause problems?
    return tmux_nm, mp_name


def mount_drive(email_address, drive_name, options=base_mount_options):
    mp_name, tmux_nm = get_mountpoint_tmux_name(email_address, drive_name)
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
        return success, error


def list_paths_mount():
    # todo basically prime start mount so that it's not super laggy when first flying
    # todo look into
    # todo lots of folks rc vfs/refresh recursive=true
    raise NotImplementedError


def list_active_drive_mounts():
    raise NotImplementedError


def get_user_shortcode(email_address):
    return _read_shortcodes()[email_address]


def set_user_shortcode(email_address, shortcode=None):
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
    raise NotImplementedError
