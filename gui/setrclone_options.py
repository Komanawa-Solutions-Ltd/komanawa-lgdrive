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
        self.setWindowTitle('Google Path support')
        self.resize(500, 100)
        self.lgdrive = LGDrive()
        # frame box
        vert = QtWidgets.QVBoxLayout()
        self.font = QtGui.QFont()
        self.sheetstyle = f"color: black; "

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
        self.setLayout(vert)
        self.show()

    def set_mount_options(self):
        # todo kinda need a popup window that says remounting drives... or something
        self.submitClicked.emit([self.remount.isChecked(), self.mount_options.currentText()])
        self.close()
