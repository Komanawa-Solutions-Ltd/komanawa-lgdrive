"""
created matt_dumont 
on: 9/11/23
"""

from PyQt6 import QtGui, QtWidgets, QtCore
from utils.base_functions import ava_mount_options
from utils.util_functions import LGDrive
from path_support import mount_options_path, icon_path


class SetMntOptions(QtWidgets.QWidget):
    submitClicked = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.setWindowTitle('Rclone Mount Options')
        self.resize(500, 100)
        self.lgdrive = LGDrive()
        # frame box
        vert = QtWidgets.QVBoxLayout()
        self.font = QtGui.QFont()
        self.sheetstyle = f"color: black; "

        lab = QtWidgets.QLabel('Rclone Mount Options')
        lab.setFont(self.font)
        lab.setStyleSheet(self.sheetstyle)
        vert.addWidget(lab)
        t = self.lgdrive.get_google_client()
        if t == '':
            t = 'default'
        self.current_id = t
        self.idlab = lab = QtWidgets.QLabel(f'Using google client: {t}')
        lab.setFont(self.font)
        lab.setStyleSheet(self.sheetstyle)
        vert.addWidget(lab)
        but = QtWidgets.QPushButton('change google client')
        but.clicked.connect(self.change_google_client)
        vert.addWidget(but)

        label = QtWidgets.QLabel(f'you can make bespoke mount options in:\n'
                                 f'  ~/{mount_options_path.relative_to(mount_options_path.home())}')
        label.setFont(self.font)
        label.setStyleSheet(self.sheetstyle)
        vert.addWidget(label)

        label = QtWidgets.QLabel('mount option:')
        label.setFont(self.font)
        label.setStyleSheet(self.sheetstyle)
        vert.addWidget(label)
        self.mount_options = QtWidgets.QComboBox()
        self.mount_options.addItems(ava_mount_options)
        vert.addWidget(self.mount_options)
        self.remount = QtWidgets.QCheckBox()
        self.remount.setText('remount drives with new options?')
        self.remount.setFont(self.font)
        self.remount.setStyleSheet("color:black")
        vert.addWidget(self.remount)
        horz = QtWidgets.QHBoxLayout()
        b = QtWidgets.QPushButton('set')
        b.clicked.connect(self.set_mount_options)
        horz.addWidget(b)
        b = QtWidgets.QPushButton('cancel')
        b.clicked.connect(self.close)
        horz.addWidget(b)
        vert.addLayout(horz)
        self.progress_lab = lab = QtWidgets.QLabel('')
        lab.setFont(self.font)
        lab.setStyleSheet(self.sheetstyle)
        vert.addWidget(lab)
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setGeometry(200, 80, 250, 20)
        self.progress.hide()
        vert.addWidget(self.progress)
        self.setLayout(vert)
        self.show()

    def set_mount_options(self):
        self.submitClicked.emit([(self.progress, self.progress_lab), self.remount.isChecked(), self.mount_options.currentText()])
        self.close()

    def change_google_client(self):
        self.sub_window_chcode = SetGoogleClient(self.current_id)
        self.sub_window_chcode.submitClicked.connect(self.set_google_client)
        self.sub_window_chcode.show()

    def set_google_client(self, data):
        client_id, client_secret = data
        if client_id is None:
            return
        self.lgdrive.set_google_client(client_id, client_secret)
        self.current_id = client_id
        self.idlab.setText(f'Using google client: {client_id}')
        self.sub_window_chcode.close()
        self.sub_window_chcode = None
        self.show()


class SetGoogleClient(QtWidgets.QWidget):
    submitClicked = QtCore.pyqtSignal(list)

    def __init__(self, currentid):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.setWindowTitle('Set google client ID')
        self.resize(500, 100)
        vert = QtWidgets.QVBoxLayout()
        self.font = QtGui.QFont()
        self.sheetstyle = f"color: black; "
        lab = QtWidgets.QLabel(f'Set google client ID\n  Currently useing:{currentid}')
        lab.setFont(self.font)
        lab.setStyleSheet(self.sheetstyle)
        vert.addWidget(lab)

        # add a link to the rclone instructions
        label = QtWidgets.QLabel()
        label.setFont(self.font)
        label.setStyleSheet(self.sheetstyle)
        label.setText(
            'Instructions to a google client ID: <a href="https://rclone.org/drive/#making-your-own-client-id">'
            'https://rclone.org/drive/#making-your-own-client-id</a>')
        label.setOpenExternalLinks(True)
        vert.addWidget(label)

        hort = QtWidgets.QHBoxLayout()
        hort2 = QtWidgets.QHBoxLayout()
        lab = QtWidgets.QLabel('client ID:')
        lab.setFont(self.font)
        lab.setStyleSheet(self.sheetstyle)
        hort.addWidget(lab)

        self.client_id = QtWidgets.QLineEdit()
        self.client_id.setFont(self.font)
        self.client_id.setStyleSheet(self.sheetstyle)
        hort2.addWidget(self.client_id)
        lab = QtWidgets.QLabel('client secret:')
        lab.setFont(self.font)
        lab.setStyleSheet(self.sheetstyle)
        hort.addWidget(lab)
        self.client_secret = QtWidgets.QLineEdit()
        self.client_secret.setFont(self.font)
        self.client_secret.setStyleSheet(self.sheetstyle)
        hort2.addWidget(self.client_secret)
        vert.addLayout(hort)
        vert.addLayout(hort2)

        horz = QtWidgets.QHBoxLayout()
        b = QtWidgets.QPushButton('set')
        b.clicked.connect(self.set)
        horz.addWidget(b)
        b = QtWidgets.QPushButton('cancel')
        b.clicked.connect(self.quit)
        horz.addWidget(b)
        vert.addLayout(horz)

        self.setLayout(vert)
        self.show()

    def set(self):
        clientid = self.client_id.text()
        clientsecret = self.client_secret.text()
        if clientid == '' or clientsecret == '':
            mbox = QtWidgets.QMessageBox()
            mbox.setWindowIcon(QtGui.QIcon(str(icon_path)))
            mbox.setWindowTitle('whoops!')
            mbox.setText('you need to enter a client id and secret')
            mbox.setFont(self.font)
            mbox.setStyleSheet(self.sheetstyle)
            mbox.exec()
            return
        self.submitClicked.emit([self.client_id.text(), self.client_secret.text()])
        self.close()

    def quit(self):
        self.submitClicked.emit([None, None])
        self.close()
