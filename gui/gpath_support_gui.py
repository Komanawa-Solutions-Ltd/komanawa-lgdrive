"""
created matt_dumont 
on: 9/11/23
"""
from PyQt6 import QtGui, QtWidgets, QtCore
from utils.util_functions import LGDrive
from path_support import icon_path


# keynote this class can be changed in the gooogle_drive_tray_pyqt class call to allow user specific
#  path management
class Gpath(QtWidgets.QWidget):
    submitClicked = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.setWindowTitle('Google Path support')
        self.resize(500, 100)
        self.lgdrive = LGDrive()
        # frame box
        vert = QtWidgets.QVBoxLayout()

        # set font stats
        self.font = QtGui.QFont()
        self.sheetstyle = f"color: black; "

        label = QtWidgets.QLabel('Drive Path')
        label.setFont(self.font)
        label.setStyleSheet(self.sheetstyle)
        vert.addWidget(label)
        horz = QtWidgets.QHBoxLayout()
        self.path = t = QtWidgets.QLineEdit('')
        horz.addWidget(t)
        b = QtWidgets.QPushButton('clear')
        b.clicked.connect(self._cleartxt)
        horz.addWidget(b)
        vert.addLayout(horz)

        label = QtWidgets.QLabel('Actions')
        label.setFont(self.font)
        label.setStyleSheet(self.sheetstyle)
        vert.addWidget(label)
        butt = self.add_buttons()
        vert.addLayout(butt)
        self.setLayout(vert)
        self.show()

    def add_buttons(self):
        """
        add buttons to the gui this is the thing to overwrite when subclassing
        :return:
        """
        buttons = {
            'Copy Google id': self.copy_gid,
            'Copy Gdive folder url': self.copy_gdrive_folder_url,
            'Open in Gdrive': self.open_in_gdrive,
            'Quit': self.quit,
        }
        layout = QtWidgets.QVBoxLayout()
        for k, v in buttons.items():
            b = QtWidgets.QPushButton(k)
            b.clicked.connect(v)
            layout.addWidget(b)
        return layout

    def _launch_error(self, message):
        mbox = QtWidgets.QMessageBox()
        mbox.setWindowIcon(QtGui.QIcon(str(icon_path)))
        mbox.setWindowTitle('Whoops!')
        mbox.setText(message)
        mbox.setFont(self.font)
        mbox.setStyleSheet(self.sheetstyle)
        mbox.exec()
        return

    def _cleartxt(self):
        self.path.setText('')

    @staticmethod
    def _to_clipboard(txt):
        cb = QtWidgets.QApplication.clipboard()
        cb.setText(txt)

    def copy_gid(self):
        try:
            t = self.lgdrive.get_google_id(self.path.text())
            self._to_clipboard(t)
        except Exception as val:
            self._launch_error(str(val))

    def copy_gdrive_folder_url(self):
        try:
            t = self.lgdrive._open_in_google_drive(self.path.text(), False)
            self._to_clipboard(t)
        except Exception as val:
            self._launch_error(str(val))

    def open_in_gdrive(self):
        try:
            t = self.lgdrive._open_in_google_drive(self.path.text(), True)
        except Exception as val:
            self._launch_error(str(val))

    def quit(self):
        self.submitClicked.emit('dummy')
        self.close()
