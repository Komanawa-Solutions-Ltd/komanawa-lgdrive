"""
created matt_dumont 
on: 17/09/23
"""
from pathlib import Path
import subprocess
import webbrowser
from path_support import google_mount_dir, mount_options_path
from base_functions import join_character, get_rclone_config, get_drive_export_format, add_user_set_shortcode, \
    update_master_config, create_config, get_user_shortcode, read_shortcodes, write_shortcodes, check_shortcode, \
    user_authenticated, list_users, get_prebuilt_mount_options, get_user_from_shortcode, list_active_drive_mounts, \
    list_drives_available, unmount_drive, close_google_drive, mount_drive, get_email_from_mountpoint_tmux_name


class lgdrive():
    def __init__(self):
        pass

    def start_google_drive(self):
        """
        start google drive, this is what gets called at start of session
        :return:
        """
        self.recreate_all_configs()
        self._mnt_previous_drives()

    def stop_google_drive(self):
        """
        stop google drive, this is what gets called at end of session
        :return:
        """
        close_google_drive()

    @staticmethod
    def add_user(user, short_code):
        """
        add the user and shortcode, update the master config, then create the config
        :param user:
        :param short_code:
        :return:
        """
        success, mssage = add_user_set_shortcode(user, short_code)
        assert success, mssage
        update_master_config(add_email=user, remove_email=None)
        success, message = create_config(user)
        assert success, message

    @staticmethod
    def recreate_all_configs():
        """
        recreate all configs, re-run to get all drives and at start of each session
        :return:
        """
        users = read_shortcodes().keys()
        all_success = True
        errors = {}
        for user in users:
            success, message = create_config(user)
            if not success:
                all_success = False
                errors[user] = message
        assert all_success, ('errors in creating configs:\n' + ' * '
                             + '\n * '.join([f'{k}: {v}' for k, v in errors.items()]))

    @staticmethod
    def rm_user(user=None):
        """
        remove the user and shortcode, update the master config, then delete the user specific config
        :param user:
        :return:
        """
        get_rclone_config(user=user).unlink(missing_ok=True)
        update_master_config(add_email=None, remove_email=user)
        shortcodes = read_shortcodes()
        ushort_code = shortcodes.pop(user)
        all_mnts = list_active_drive_mounts()
        mnts = [e for e in all_mnts if ushort_code == e.split(join_character)[0]]
        for mnt in mnts:
            unmount_drive(mnt)
        write_shortcodes(shortcodes)

    def rm_all_users(self):
        """
        remove all users
        :return:
        """
        users = list_users()
        for user in users:
            self.rm_user(user)

    def change_shortcode(self, user, new_shortcode):
        """
        change the shortcode for a given user
        :param user: email address
        :param new_shortcode: new shortcode
        :return:
        """
        short_codes = read_shortcodes()
        old_shortcode = get_user_shortcode(user)
        success, mssage = check_shortcode(new_shortcode, short_codes)
        if success:
            mnted_drives = list_active_drive_mounts()
            mnted_drives = [e for e in mnted_drives if
                            old_shortcode == get_email_from_mountpoint_tmux_name(mp_name=e)[1]]
            for d in mnted_drives:
                unmount_drive(d)
            short_codes[user] = new_shortcode
            write_shortcodes(short_codes)
            for d in mnted_drives:
                mount_drive(d.replace(old_shortcode, new_shortcode))
        else:
            raise ValueError(f'failed to change shortcode for {user} to {new_shortcode}, keeping {old_shortcode} '
                             f'instead.\nError: {mssage}')

    @staticmethod
    def reauthenticate_user(user):
        """
        re authenicate an existing user
        :param user:
        :return:
        """
        users = list_users()
        assert user in users, f'{user} not in {users}'
        if user_authenticated(user):
            pass
        else:
            update_master_config(add_email=user, remove_email=None)
            success, message = create_config(user)
            assert success, message

    def set_mount_options(self, option_name, remount=False):
        """
        set the mount options to a prebuilt option
        :param option_name: one of the prebuilt options ('light', 'default')
        :param remount:
        :return:
        """
        t = get_prebuilt_mount_options(option_name)
        mount_options_path.write_text(t)
        print(f'mount options set to {option_name}')
        if remount:
            self.stop_google_drive()
            self.start_google_drive()

    @staticmethod
    def ls_users(detailed=False):
        """
        list all users
        :return:
        """
        users = list_users()
        if not detailed:
            print(f'users:\n * ' + '\n * '.join(users))
            return
        out = []
        for user in users:
            temp = {}
            temp['short_code'] = sc = get_user_shortcode(user)
            temp['authenticated'] = user_authenticated(user)
            mounted = [e for e in list_active_drive_mounts() if sc in e]
            temp['nmounted'] = len(mounted)
            temp['mounted'] = mounted
            temp = '\n    * ' + '\n    * '.join([f'{k}: {v}' for k, v in temp.items()])
            out.append(f'{user}: {temp}')
        out = '\n * '.join(out)
        print(f'users:\n * {out}')

    @staticmethod
    def ls_pos_drives(user=None, short_code=None):
        """
        list all possible drives for a given user
        :return:
        """
        if user is None:
            user = get_user_from_shortcode(short_code)
        users = list_users()
        assert user is not None, 'must provide either user or short_code'
        assert user in users, f'{user} not in {users}'
        drives = list_drives_available(user)
        print(f'drives for {user}:\n * ' + '\n * '.join(drives))

    @staticmethod
    def ls_mnt_drives():
        """
        list all mounted drives
        :return:
        """
        mt_drives = list_active_drive_mounts()
        print(f'mounted drives:\n * ' + '\n * '.join(mt_drives))

    def mount_drive(self, drivenm):
        """
        mount a drive
        :param drivenm:
        :return:
        """
        mount_drive(drivenm)

    def unmount_drive(self, drivenm):
        """
        unmount a drive
        :param drivenm: drive name (shortcode + drive name)
        :return:
        """
        mnts = list_active_drive_mounts()
        if drivenm in mnts:
            unmount_drive(drivenm)
        else:
            print(f'{drivenm} was not mounted')

    @staticmethod
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

    def print_glink(self, path):
        """
        prints the google drive link for a file or folder
        :param path: path to file or folder
        :return:
        """
        link = self._open_in_google_drive(path, open=False)
        print(link)

    def open_glink(self, path):
        """
        opens the google drive link for a file or folder
        :param path: path to file or folder
        :return:
        """
        self._open_in_google_drive(path, open=True)

    def _open_in_google_drive(self, path, open=True):
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
        gid, mtype = self.get_google_id(path)
        link = f'https://drive.google.com/drive/folders/{gid}'
        if open:
            webbrowser.open(link, new=0, autoraise=True)
        else:
            return link

    def _mnt_previous_drives(self):  # todo
        """
        mount all previous drives
        :return:
        """
        raise NotImplementedError
# todo user pyfire https://github.com/google/python-fire/ to make CLI
