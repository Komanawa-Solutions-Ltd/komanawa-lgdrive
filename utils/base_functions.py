"""
created matt_dumont 
on: 17/09/23
"""
import re
import time
import subprocess
from path_support import google_mount_dir, google_cache_dir, base_configs, short_code_path, mount_options_path, \
    master_config, mounted_drives_path

join_character = '@'
bad_shortcode_char = (' ', '\t', '\n', '\r', '/', '\\', '?', '<', '>', '|', ':', '*', '"', "'", '=', join_character)
base_tmux_name = f'*gd{join_character}' + '{}' + join_character + '{}'

ava_mount_options = (
    'default',
    'light',
)

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
    assert key in ava_mount_options, f'{key=} must be one of {ava_mount_options}'
    if key == 'light':
        return light_mount_option
    elif key == 'default':
        return base_mount_options
    else:
        raise ValueError("shouldn't get here")


def close_google_drive():
    """ unmount all drives, raise if drives are still mounted"""
    mount_names = list_active_drive_mounts()
    for nm in mount_names:
        if is_mounted(nm):
            unmount_drive(nm, rm_from_drive_list=False)

    for nm in mount_names:
        if is_mounted(nm):
            raise ValueError(f'{nm} is still mounted')
    return True


def _get_config_path(email_address=None, short_code=None):
    if email_address is None and short_code is None:
        raise ValueError('must provide email_address or short_code')
    elif email_address is not None and short_code is not None:
        raise ValueError('must provide email_address or short_code, not both')
    if short_code is None:
        short_code = get_user_shortcode(email_address)
    if email_address is None:
        email_address = get_user_from_shortcode(short_code)
    config_name = f'.{short_code}.rclone.conf'
    config_path = base_configs.joinpath(config_name)
    return config_path


def get_rclone_config(email_address=None, short_code=None, recreate_config=False):
    config_path = _get_config_path(email_address, short_code)
    if email_address is None:
        email_address = get_user_from_shortcode(short_code)
    assert email_address is not None
    if recreate_config:
        create_config(email_address)
    return config_path


def create_config(email_address):
    """
    create a config file for a given email address
    :param email_address:
    :return:
    """
    possible_drives = list_drives_available(email_address)
    assert len(possible_drives) > 0, f'no drives available for {email_address}'
    config_path = _get_config_path(email_address=email_address)

    # add all drives to config
    token = get_token(email_address)
    with open(config_path, 'w') as f:
        for drive_nm, drive_info in possible_drives.items():
            teamid = drive_info['id']
            out_text_team = (
                '#start\n'
                f"[{drive_nm}]\n"
                'type = drive\n'
                'scope = drive\n'
                f'token = {token}\n'
                f'team_drive ={teamid}\n'
                'root_folder_id =\n'
                '#end\n\n')
            f.write(out_text_team)
    config_path.chmod(600)


def get_auth_code(email_address, local=True):
    code = 'rclone authorize "drive"'
    if local:
        output = subprocess.run(code, capture_output=True, shell=True)
        assert output.returncode == 0, f'failed to authenticate {email_address}'
        output = output.stdout.decode()
    else:
        output = []
        code += ' --auth-no-open-browser'
        process = subprocess.Popen(code, shell=True, stdout=subprocess.PIPE)
        print_output = True
        while process.poll() is None:
            nextline = process.stdout.readline()
            if nextline == '':
                continue
            t = nextline.decode().strip()
            output.append(t)
            if 'paste' in t.lower():
                print_output = False
            if print_output:
                print(t)
            output = '\n'.join(output)

    output = output[output.find('{'):output.find('}') + 1]
    return output


def is_mounted(nm):
    """
    check drive nm is mounted (by looking for tmux env
    :param nm:
    :return:
    """
    mounted = False
    time.sleep(1)
    raw_drive_name, shortcode = get_email_from_mountpoint_tmux_name(mp_name=nm)
    # check if tmux session exists
    tmux_nm, mp_name = get_mountpoint_tmux_name(raw_drive_name, shortcode=shortcode)
    assert mp_name == nm, f'{mp_name=} != {nm=}'
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


def get_mnt_name_from_tmux_name(tmux_name):
    return join_character.join(tmux_name.split(join_character)[1:])


def get_tmuxnm_from_mnt_name(mnt_name):
    shortcode, raw_drive_name = mnt_name.split(join_character)
    return base_tmux_name.format(shortcode, raw_drive_name)


def get_mountpoint_tmux_name(raw_drive_name, shortcode=None, email_address=None):
    raw_drive_name = raw_drive_name.replace(' ', '_')
    if shortcode is None and email_address is None:
        raise ValueError('must provide shortcode or email_address')

    if shortcode is None:
        shortcode = get_user_shortcode(email_address)
    assert shortcode is not None
    tmux_nm = base_tmux_name.format(shortcode, raw_drive_name)
    mp_name = join_character.join([shortcode, raw_drive_name])
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


def mount_drive(drivenm, recreate_config=False):
    """
    mount a google drive in a tmux session
    :param drivenm: drive name (shortcode + drive name)
    :param recreate_config: bool if true recreate config file
    :return:
    """
    options = read_options()
    tmux_nm = get_tmuxnm_from_mnt_name(drivenm)
    raw_drive_name, shortcode = get_email_from_mountpoint_tmux_name(tmux_name=tmux_nm)
    pos_drives = list_drives_available(shortcode=shortcode)
    config_path = get_rclone_config(short_code=shortcode, recreate_config=recreate_config)
    assert drivenm in pos_drives, f'{drivenm} not in {pos_drives}'
    config_drives = list_drives_in_config(config_path)
    if drivenm not in config_drives:
        get_rclone_config(short_code=shortcode, recreate_config=True)

    if is_mounted(drivenm):
        print(f'skipping {raw_drive_name} already mounted')
    else:
        mount_dir = google_mount_dir.joinpath(drivenm)
        mount_dir.mkdir(parents=True, exist_ok=True)
        cache = google_cache_dir.joinpath(drivenm)
        cache.mkdir(exist_ok=True)
        assert mount_dir.is_dir(), f'mount_dir {mount_dir} is not a dir'
        assert len(list(mount_dir.iterdir())) == 0, f'mount_dir {mount_dir} is not empty'

        # create tmux session for the mount then mount the drive.
        code = ' '.join([
            f"tmux new -s {tmux_nm} -d",  # run in tmux
            f'rclone -v',
            f'--config {config_path}',  # email specific config file
            f'--cache-dir {cache}',  # cache dir
            *options,  # mount options
            f'mount {drivenm}:  {mount_dir}'])
        subprocess.run(code, shell=True)
        success = True
        error = ''
        if not is_mounted(drivenm):
            success = False
            error = f'mount failed for {drivenm}'
        # write to mounted drives file
        if success:
            update_mounted_drives(add_drive=drivenm)
        prime_mount(tmux_nm)
        return success, error


def prime_mount(tmux_name):
    # todo basically prime start mount so that it's not super laggy when first flying
    # todo lots of folks rc vfs/refresh recursive=true
    pass


def list_active_drive_mounts():
    """
    list all active drive mounts
    :return: list of tmux dirs
    """
    tmuxdirs = subprocess.run('tmux ls', capture_output=True, shell=True).stdout.decode()
    tmuxdirs = tmuxdirs.split('\n')
    tmuxdirs = [e.split(':')[0] for e in tmuxdirs]
    base_name = base_tmux_name.split('{')[0]
    tmuxdirs = [e for e in tmuxdirs if base_name == e[:len(base_name)]]
    mnt_names = [get_mnt_name_from_tmux_name(e) for e in tmuxdirs]
    return mnt_names


def user_authenticated(email_address=None, shortcode=None):
    try:
        if email_address is not None:
            list_drives_available(email_address)
        elif shortcode is not None:
            list_drives_available(get_user_from_shortcode(shortcode))
        else:
            raise ValueError('must provide email_address or shortcode')
        return True
    except AssertionError:
        return False


def get_user_shortcode(email_address):
    return read_shortcodes()[email_address]


def check_shortcode(shortcode, short_codes=None):
    if short_codes is None:
        short_codes = read_shortcodes()
    inv = {v: k for k, v in short_codes.items()}
    success = True
    mssage = ''
    if shortcode in short_codes.values():
        success = False
        mssage = f'{shortcode} already in use for {inv[shortcode]}'
    elif any([e in shortcode for e in bad_shortcode_char]):
        success = False
        mssage = f'bad characters in {shortcode}, cannot use {bad_shortcode_char}'
    elif shortcode[0] == '-':
        success = False
        mssage = f'cannot start with "-"'
    return success, mssage


def add_user_set_shortcode(email_address, shortcode=None):
    # short code to prepend to the mount name (e.g. hm for home users), user defined
    if shortcode is None:
        shortcode = email_address.split('@')[0]
    short_codes = read_shortcodes()
    success, mssage = check_shortcode(shortcode, short_codes)
    if success:
        short_codes[email_address] = shortcode
        write_shortcodes(short_codes)
    return success, mssage


def get_user_from_shortcode(shortcode):
    t = read_shortcodes()
    t = {v: k for k, v in t.items()}
    return t[shortcode]


def read_shortcodes():
    if not short_code_path.exists():
        return {}
    with short_code_path.open('r') as f:
        lines = f.readlines()
    out = {}
    for line in lines:
        line = line.strip('\n')
        line = line.split('=')
        out[line[0]] = line[1]
    return out


def write_shortcodes(short_codes):
    with short_code_path.open('w') as f:
        for k, v in short_codes.items():
            f.write(f'{k}={v}\n')
    short_code_path.chmod(600)

def list_drives_available(email_address=None, shortcode=None):
    """
    get possible drives that could be mounted for a given email address
    :param email_address:
    :return: dict of drive names and info
    {drivename(inc short code): {id:###, kind:###, name:###(w/o shortcode), shortcode:###}}
    """
    if shortcode is None:
        assert email_address is not None
        shortcode = get_user_shortcode(email_address)
    if email_address is None:
        assert shortcode is not None
        email_address = get_user_from_shortcode(shortcode)
    assert email_address is not None, 'must provide shortcode or email_address'
    assert shortcode is not None, 'must provide shortcode or email_address'

    code = ' '.join(['rclone',
                     'backend',
                     'drives',
                     '--config', str(master_config),
                     f'{email_address}:'
                     ])
    output = subprocess.run(code, capture_output=True, shell=True)
    assert output.returncode == 0, f'failed to list google drives for {email_address}: {output.stderr.decode()}'
    out = output.stdout.decode()
    outdata = {}
    for i, line in enumerate(out.split('\n')):
        line = line.strip()
        line = line.strip('[],')
        line = line.strip('\t')
        if line != '':
            if line =='{':
                temp = {}
                temp['shortcode'] = shortcode
            elif line == '}':
                outkey = get_mountpoint_tmux_name(temp['name'], shortcode=shortcode)[1]
                outdata[outkey] = temp
            else:
                line = line.strip(',{}')
                k = line.split(':')[0].strip(' "')
                v = line.split(':')[1].strip(' "')
                temp[k] = v
    # manually add in mydrive
    outdata[get_mountpoint_tmux_name('mydrive', shortcode=shortcode)[1]] = {
        'shortcode': shortcode,
        "id": "",
        "kind": "drive#drive",
        "name": 'mydrive'
    }
    return outdata


def write_options(options):
    with mount_options_path.open('w') as f:
        for line in options:
            f.write(line + '\n')
    mount_options_path.chmod(600)

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


def update_master_config(add_email=None, remove_email=None, local=True):
    """
    update the master config file to include add_email and remove remove_email
    :param add_email: None or email to add or re-authenticate
    :param remove_email: None or email to remove
    :param local: bool if true use local auth, else use browser auth
    :return:
    """
    master = read_master_config()
    if add_email is not None:
        if add_email in master:  # re-authenticate
            master[add_email]['token'] = get_auth_code(add_email, local=local)
        else:
            temp = {'type': 'drive',
                    'scope': 'drive',
                    'token': get_auth_code(add_email, local=local),
                    'team_drive': '',
                    'root_folder_id': ''
                    }
            master[add_email] = temp
    if remove_email is not None:
        if remove_email in master:
            master.pop(remove_email)

    with master_config.open('w') as f:
        for email, data in master.items():
            # write records:
            out_text = (
                '#start\n'
                f"[{email}]\n"
                f'type = {data["type"]}\n'
                f'scope = {data["scope"]}\n'
                f'token = {data["token"]}\n'
                f'team_drive = {data["team_drive"]}\n'
                f'root_folder_id = {data["root_folder_id"]}\n'
                '#end\n\n')
            f.write(out_text)
    master_config.chmod(600)

def read_master_config():
    """
    read the master config file
    :return:
    """
    out = {}
    if not master_config.exists():
        return out
    with master_config.open('r') as f:
        lines = f.readlines()
    lines = [e.strip('\n') for e in lines]
    lines = [e for e in lines if e != '']
    i = 0
    email = None
    temp = None
    for line in lines:
        if line == '#start':
            i += 1
            temp = {}
        elif line == '#end':
            out[f'{email}'] = temp
            i = 0
        elif i == 1:
            email = line.strip('[]')
            i += 1
        else:
            line = line.split('=')
            temp[line[0].strip()] = line[1].strip()
            i += 1
    return out


def get_token(email_address):
    master_config_data = read_master_config()
    assert email_address in master_config_data, f'{email_address} not in {master_config_data}'
    return master_config_data[email_address]['token']


def list_users():
    return list(read_shortcodes().keys())


def unmount_drive(nm, rm_from_drive_list=True):
    mount_dir = google_mount_dir.joinpath(nm)
    code = f"umount {mount_dir}"
    output = subprocess.run(code, shell=True)
    if rm_from_drive_list:
        update_mounted_drives(remove_drive=nm)
    return output.returncode == 0


def read_mounted_drives():
    """
    read the list of mounted drives
    :return:
    """
    if not mounted_drives_path.exists():
        return []
    with mounted_drives_path.open('r') as f:
        lines = f.readlines()
    lines = [e.strip('\n') for e in lines]
    return list(set(lines))


def update_mounted_drives(add_drive=None, remove_drive=None):
    """
    update the list of mounted drives
    :return:
    """
    mnt_dirs = read_mounted_drives()
    if add_drive is not None:
        mnt_dirs.append(add_drive)
    if remove_drive is not None:
        if remove_drive in mnt_dirs:
            mnt_dirs.remove(remove_drive)
    mnt_dirs = list(set(mnt_dirs))
    with mounted_drives_path.open('w') as f:
        for line in mnt_dirs:
            f.write(line + '\n')
    mounted_drives_path.chmod(600)

def list_drives_in_config(config_path):
    with config_path.open('r') as f:
        lines = f.read()
    t = re.findall("\[([^]]+)\]", lines)
    return t

def get_id_from_config(drive_name, config_path):
    with config_path.open('r') as f:
        lines = f.readlines()
    look_for_id = False
    for l in lines:
        if drive_name in l:
            look_for_id = True
            continue
        if look_for_id:
            if 'team_drive' in l:
                return l.split('=')[1].strip()
    return ''

if __name__ == '__main__':
    email = 'matt@komanawa.com'
    list_drives_in_config(get_rclone_config(email_address=email, recreate_config=False))
    mt_drives = list_active_drive_mounts()
    short_code = get_user_shortcode(email)
    mt_drives = [e for e in mt_drives if short_code in e.split(join_character)[0]]
    close_google_drive()
    pass