"""
created matt_dumont 
on: 13/10/23
"""
from PyQt6 import QtGui, QtWidgets
import sys
from pathlib import Path
from threading import Event

sys.path.append(Path(__file__).parents[1])
from lgdrive.path_support import icon_path
from lgdrive.gui.add_user_gui import AddUser, ChangeShortcode
from lgdrive.gui.add_remove_drives import AddRmDrives
from lgdrive.gui.rm_user_gui import RmUser, ReAuthUser
from lgdrive.utils.util_functions import LGDrive
from lgdrive.gui.gpath_support_gui import Gpath
from lgdrive.gui.setrclone_options import SetMntOptions


class GoogleDriveTrayApp:
    menu_keys = (
        'gpath_support',
        'set_rclone_options',
        'add_user',
        'quit',
    )
    menu_text = {
        'gpath_support': 'Drive Path Support',
        'set_rclone_options': 'Set Rclone Options',
        'add_user': 'Add User',
        'quit': 'Quit',
    }

    def __init__(self, app, gpath_support=Gpath):
        assert isinstance(gpath_support, Gpath) or issubclass(gpath_support, Gpath)
        self.font = QtGui.QFont()
        self.sheetstyle = f"color: black; "
        self.gpath_support_gui = gpath_support
        self.lgdrive = LGDrive()
        self.lgdrive.start_google_drive()
        self.event = Event()
        self.app = app
        self.tray = QtWidgets.QSystemTrayIcon()
        icon = QtGui.QIcon(str(icon_path))
        self.tray.setIcon(icon)
        self.tray.setVisible(True)
        self.create_menu()

    def create_menu(self):
        print('creating menu')
        self.menu_items = {}

        menu_actions = {
            'gpath_support': self._gpath_support,
            'set_rclone_options': self._set_rclone_options,
            'add_user': self._add_user_window,
            'quit': self.close,
        }

        self.menu = QtWidgets.QMenu()

        for u in LGDrive._get_users():
            self.menu_items[u] = t = UserMenu(u, self)
            self.menu.addMenu(t)

        for k in self.menu_keys:
            t = QtGui.QAction(self.menu_text[k])
            t.triggered.connect(menu_actions[k])
            self.menu_items[k] = t
            self.menu.addAction(t)

        self.tray.setContextMenu(self.menu)

    def _add_user_window(self):
        try:
            self.sub_window_user = AddUser(self.lgdrive._get_users())
            self.sub_window_user.submitClicked.connect(self.add_user)
            self.sub_window_user.show()
        except Exception as val:
            self._launch_error(f'error for add user:\n{val}')
            return

    def add_user(self, data):
        add, user, shortcode = data
        print(f"Adding user: {user}")
        if add:
            try:
                self.lgdrive.add_user(user, shortcode)
            except Exception as val:
                self._launch_error(f'error for add user:\n{val}')
                self.sub_window_user.close()

        self.create_menu()

    def _auth_user_window(self, user):
        try:
            self.sub_window_auth = ReAuthUser(user, self.lgdrive._user_authenticated(user))
            self.sub_window_auth.submitClicked.connect(self.authenticate_user)
            self.sub_window_auth.show()
        except Exception as val:
            self._launch_error(f'error for re-auth user:\n{val}')
            return

    def authenticate_user(self, data):
        auth, user = data
        try:
            if auth:
                self.lgdrive.reauthenticate_user(user)
        except Exception as val:
            self._launch_error(f'error for re-auth user:\n{val}')
            self.sub_window_auth.close()
        self.create_menu()

    def _set_rclone_options(self):
        try:
            self.sub_window_mnt = SetMntOptions()
            self.sub_window_mnt.submitClicked.connect(self.set_rclone_options)
            self.sub_window_mnt.show()
        except Exception as val:
            self._launch_error(f'error for set rclone options:\n{val}')
            return

    def set_rclone_options(self, data):
        (progresbar, proglab), remount, mnt_options = data
        self.lgdrive.set_mount_options(mnt_options, remount=False)
        if remount:
            drives = self.lgdrive._get_mnt_drives(None)
            i = 0
            nactions = len(drives)
            progresbar.show()
            for d in drives:
                t = f"Remounting drive: {d}"
                print(t)
                proglab.setText(t)
                progresbar.setValue(int(i / nactions * 100))
                self.lgdrive.unmount_drive(d)
                self.lgdrive.mount_drive(d)
                i += 1

    def _gpath_support(self):
        try:
            self.sub_window_gdrive = self.gpath_support_gui()
        except Exception as val:
            self._launch_error(f'error for gpath support:\n{val}')
            return

        def temp(*args):
            self.sub_window_gdrive.close()

        self.sub_window_gdrive.submitClicked.connect(temp)
        self.sub_window_gdrive.show()

    def _add_remove_drive_window(self, user):

        try:
            aval_drives = self.lgdrive._get_possible_drives(user)
            curr_drives = self.lgdrive._get_mnt_drives(user)
            aval_drives = [d for d in aval_drives if d not in curr_drives]
            self.drive_sub = AddRmDrives(user=user, current_drives=curr_drives,
                                         available_drives=aval_drives)
            self.drive_sub.submitClicked.connect(self.add_rm_drives)
            self.drive_sub.show()
        except Exception as val:
            self._launch_error(f'error for add/remove drives:\n{val}\ntry re-authenticating')

    def add_rm_drives(self, drives):
        progresbar, proglab = drives[0]
        user = drives[1]

        if len(drives) > 2:
            if drives[2] is None:
                return
            drives = drives[2:]
        else:
            drives = []

        current_drives = self.lgdrive._get_mnt_drives(user)
        add_drives = [d for d in drives if d not in current_drives]
        rm_drives = [d for d in current_drives if d not in drives]
        i = 0
        nactions = len(add_drives) + len(rm_drives)
        progresbar.show()
        for d in add_drives:
            t = f"Adding drive for {user}: {d}"
            print(t)
            proglab.setText(t)
            progresbar.setValue(int(i / nactions * 100))
            self.lgdrive.mount_drive(d)
            i += 1
        for d in rm_drives:
            progresbar.setValue(int(i / nactions * 100))
            t = f'Removing drive for {user}: {d}'
            print(t)
            proglab.setText(t)
            self.lgdrive.unmount_drive(d)
            i += 1

    def _remove_user_window(self, user):
        try:
            print(f"Removing user: {user}")
            self.sub_window_rmuser = RmUser(user)
            self.sub_window_rmuser.submitClicked.connect(self.rm_user)
            self.sub_window_rmuser.show()
        except Exception as val:
            self._launch_error(f'error for remove user:\n{val}')
            return

    def rm_user(self, data):
        rm, user = data
        if rm:
            print(f"Removing user: {user}")
            self.lgdrive.rm_user(user)
            self.create_menu()
            pass
        else:
            pass  # cancelled

    def _change_shortcode(self, user):
        try:
            print(f"changing shortcode for user: {user}")
            self.sub_window_chcode = ChangeShortcode(user, self.lgdrive._get_shortcode(user))
            self.sub_window_chcode.submitClicked.connect(self.change_shortcode)
            self.sub_window_chcode.show()
        except Exception as val:
            self._launch_error(f'error for change shortcode:\n{val}')
            return

    def change_shortcode(self, data):
        change, user, newcode = data
        if change:
            self.lgdrive.change_shortcode(user, newcode)

    def list_user_drives(self, user):
        return self.lgdrive._get_possible_drives(user)

    def _launch_error(self, message):
        mbox = QtWidgets.QMessageBox()
        mbox.setWindowIcon(QtGui.QIcon(str(icon_path)))
        mbox.setWindowTitle('whoops!')
        mbox.setText(message)
        mbox.setFont(self.font)
        mbox.setStyleSheet(self.sheetstyle)
        mbox.exec()
        return

    def close(self):
        print('closing')
        self.lgdrive.stop_google_drive()
        self.event.set()
        self.app.quit()


class UserMenu(QtWidgets.QMenu):
    def __init__(self, user, parent):
        assert isinstance(parent, GoogleDriveTrayApp)

        super().__init__()
        self.user = user
        sc = self.parent.lgdrive._get_shortcode(self.user)
        self.menu_text = {
            'auth_user': f'Re-Authenticate {user}',
            'add_remove_drive': f'Add / Remove Drive(s) for {user}',
            'remove_user': f'Remove {user}',
            'change_shortcode': f'Change Shortcode {sc}',
        }

        self.setTitle(self.user)
        self.parent = parent
        self.menu_actions = {
            'auth_user': self.auth_user,
            'change_shortcode': self.change_shortcode,
            'add_remove_drive': self.add_remove_drive,
            'remove_user': self.remove_user,

        }
        self._create_menu()

    def _create_menu(self):
        self.menu_items = {}
        for k in self.menu_text.keys():
            t = QtGui.QAction(self.menu_text[k])
            t.triggered.connect(self.menu_actions[k])
            self.menu_items[k] = t
            self.addAction(t)

    def auth_user(self):
        self.parent._auth_user_window(self.user)

    def change_shortcode(self):
        self.parent._change_shortcode(self.user)

    def remove_user(self):
        self.parent._remove_user_window(self.user)

    def add_remove_drive(self):
        self.parent._add_remove_drive_window(self.user)


def launch_panel_app():
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    GDTA = GoogleDriveTrayApp(app)
    sys.exit(app.exec())


if __name__ == '__main__':
    launch_panel_app()
