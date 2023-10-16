"""
created matt_dumont 
on: 13/10/23
"""
from PyQt6 import QtGui, QtWidgets
import sys
from pathlib import Path
from threading import Event

sys.path.append(Path(__file__).parents[1])
from path_support import icon_path, tray_app_state_path
from gui.add_user_gui import AddUser
from gui.add_remove_drives import AddRmDrives
from gui.rm_user_gui import RmUser

# todo GUI is good enough for now, next step is the funcitonality.

class GoogleDriveTrayApp:
    menu_keys = (
        'add_user',
        'quit',
    )
    menu_text = {
        'add_user': 'Add User',
        'quit': 'Quit',
    }

    def __init__(self, app):
        tray_app_state_path.unlink(True)  # todo DADB
        if tray_app_state_path.exists():
            with open(tray_app_state_path, 'r') as f:
                pass  # todo read state
            self.users = []  # todo set
            self.user_drives = {}  # todo set
            self.users_authenticated = {u: self.test_user_auth(u) for u in self.users}
            raise NotImplementedError
        else:
            self.user_drives = {
                'test@test.com': []  # todo DADB
            }
            self.users = [
                'test@test.com'  # todo DADB
            ]
            self.users_authenticated = {
                'test@test.com': True  # todo DADB
            }

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
            'add_user': self._add_user_window,
            'quit': self.close,
        }

        self.menu = QtWidgets.QMenu()

        for u in self.users:
            self.menu_items[u] = t = UserMenu(u, self)
            self.menu.addMenu(t)

        for k in self.menu_keys:
            t = QtGui.QAction(self.menu_text[k])
            t.triggered.connect(menu_actions[k])
            self.menu_items[k] = t
            self.menu.addAction(t)

        self.tray.setContextMenu(self.menu)

    def _add_user_window(self):
        self.sub_window_user = AddUser(self.users)
        self.sub_window_user.submitClicked.connect(self.add_user)
        self.sub_window_user.show()

    def add_user(self, user):
        print(f"Adding user: {user}")
        self.user_drives[user] = []
        self.users.append(user)
        self.users_authenticated[user] = False
        # todo enable when ready self._auth_user_window(user)
        self.create_menu()

    def _auth_user_window(self, user):  # todo
        # todo then authenticate
        raise NotImplementedError

    def authenticate_user(self):
        # todo authenticate user... how to do this?
        self.create_menu()

    def _add_remove_drive_window(self, user):

        self.drive_sub = AddRmDrives(user=user,
                                     current_drives=self.user_drives[user],
                                     available_drives=self.list_user_drives(user))
        self.drive_sub.submitClicked.connect(self.add_rm_drives)
        self.drive_sub.show()

    def add_rm_drives(self, drives):
        user = drives[0]
        if len(drives) > 1:
            if drives[1] is None:
                return

            print(f"Adding drives for {user}: {drives[1:]}")
            # todo do stuff

        else:
            print(f'removing all drives for: {user}')
            # todo do stuff

    def _remove_user_window(self, user):
        print(f"Removing user: {user}")
        self.sub_window_rmuser = RmUser(user)
        self.sub_window_rmuser.submitClicked.connect(self.rm_user)
        self.sub_window_rmuser.show()

    def rm_user(self, data):
        rm, user = data
        if rm:
            # todo remove user from rclone etc.
            print(f"Removing user: {user}")
            self.users.remove(user)
            self.user_drives.pop(user)
            self.users_authenticated.pop(user)
            self.create_menu()
            pass
        else:
            pass  # cancelled

    def list_user_drives(self, user):  # todo user rclone
        # todo look at: https://forum.rclone.org/t/google-drive-list-shared-drives/22955
        # todo remove current drives for the user
        out = [f'test{i}' for i in range(10)]  # todo dadb
        return out

    def test_user_auth(self, user):  # todo
        raise NotImplementedError

    def close(self):

        # todo handle unmounting drives
        # todo handle saving state
        with open(tray_app_state_path, 'w') as f:
            pass  # todo read/write state
        self.event.set()
        self.app.quit()
        pass


class UserMenu(QtWidgets.QMenu):  # todo add color for authenicated or not, transmitting??? mouseover???
    def __init__(self, user, parent):
        assert isinstance(parent, GoogleDriveTrayApp)

        super().__init__()
        self.user = user
        self.menu_text = {
            'auth_user': f'Authenticate {user}',
            'add_remove_drive': f'Add / Remove Drive(s) for {user}',
            'remove_user': f'Remove {user}',
        }

        self.setTitle(self.user)
        self.parent = parent
        self.menu_actions = {
            'auth_user': self.auth_user,
            'add_remove_drive': self.add_remove_drive,
            'remove_user': self.remove_user,
        }
        self._create_menu()

    def _create_menu(self):
        self.menu_items = {}
        for k in self.menu_text.keys():
            t = QtGui.QAction(self.menu_text[k])
            t.triggered.connect(self.menu_actions[k])
            if k == 'auth_user':
                t.setEnabled(not self.parent.users_authenticated[self.user])
            self.menu_items[k] = t
            self.addAction(t)

    def auth_user(self):
        self.parent._auth_user_window(self.user)

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
