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


class GoogleDriveTrayApp:
    menu_keys = (
        'add_user',
        'auth_user',
        'add_remove_drive',
        'remove_user',
        'quit',
    )
    menu_text={
        'add_user':'Add User',
        'auth_user':'Authenticate User',
        'add_remove_drive':'Add / Remove Drive(s)',
        'remove_user':'Remove User',
        'quit':'Quit',
    }


    def __init__(self, app):
        if tray_app_state_path.exists():
            with open(tray_app_state_path, 'r') as f:
                pass  # todo read/write state

        self.user_drives = {}
        self.users = []
        self.users_authenticated = []

        # todo test that the users are authenticated

        self.event = Event()
        self.app = app
        self.tray = QtWidgets.QSystemTrayIcon()
        icon = QtGui.QIcon(str(icon_path))
        self.tray.setIcon(icon)
        self.tray.setVisible(True)
        self._create_menu()
        self.tray.setContextMenu(self.menu)



    def _create_menu(self):
        self.menu_items = {}
        menu_actions={
            'add_user':self._add_user_window,
            'auth_user':self._auth_user_window,
            'add_remove_drive':self._add_remove_drive_window,
            'remove_user':self._remove_user_window,
            'quit':self.close,
        }

        self.menu = QtWidgets.QMenu()

        for k in self.menu_keys:
            t = QtGui.QAction(self.menu_text[k])
            t.triggered.connect(menu_actions[k])
            self.menu_items[k] = t
            self.menu.addAction(t)

    def _add_user_window(self): # todo tray working this likange is not... next step
        self.sub_window = AddUser(self.users)
        self.sub_window.submitClicked.connect(self.add_user)
        self.sub_window.show()

    def add_user(self, user):
        print(f"Adding user: {user}")
        self.user_drives[user] = []
        self.users.append(user)
        self._auth_user_window(user)


    def _auth_user_window(self, start_user): # todo
        # todo dropdown window to select user then authenticate
        raise NotImplementedError

    def _add_remove_drive_window(self): # todo start here???
        raise NotImplementedError

    def _remove_user_window(self): # todo
        raise NotImplementedError

    def close(self):

        # todo handle unmounting drives
        # todo handle saving state
        with open(tray_app_state_path, 'w') as f:
            pass  # todo read/write state
        self.event.set()
        self.app.quit()
        pass


def launch_panel_app():
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    GDTA = GoogleDriveTrayApp(app)
    sys.exit(app.exec())

if __name__ == '__main__':
    launch_panel_app()