"""
created matt_dumont
on: 7/10/23
"""
import datetime
from copy import deepcopy
import sys
from PyQt6 import QtGui, QtWidgets, QtCore


class AddUser(QtWidgets.QWidget):
    submitClicked = QtCore.pyqtSignal(str)

    def __init__(self, existing_users):
        super().__init__()
        for u in existing_users:
            assert type(u) == str
            assert '@' in u
            assert u == u.lower()
        self.existing_users = deepcopy(existing_users)

        self.resize(100, 100)
        # frame box
        vert = QtWidgets.QVBoxLayout()

        # set font stats
        self.font = QtGui.QFont()
        self.sheetstyle = f"color: black; "

        label = QtWidgets.QLabel('User Email Address')
        label.setFont(self.font)
        label.setStyleSheet(self.sheetstyle)
        vert.addWidget(label)
        self.answers = t = QtWidgets.QLineEdit('')
        vert.addWidget(t)
        # save/cancel buttons
        save = QtWidgets.QPushButton('Add User')
        save.clicked.connect(self.save)
        cancel = QtWidgets.QPushButton('Cancel')
        cancel.clicked.connect(self.close)
        horiz = QtWidgets.QHBoxLayout()
        horiz.addWidget(save)
        horiz.addWidget(cancel)
        vert.addLayout(horiz)
        self.setLayout(vert)
        self.show()

    def save(self):
        txt = self.answers.text().strip().lower()
        problem = False
        if '@' not in txt:
            problem = True
            mssage = 'Email address must contain an @ symbol'

        if txt in self.existing_users:
            problem = True
            mssage = 'Email address already exists'

        if problem:
            mbox = QtWidgets.QMessageBox()
            mbox.setText(mssage)
            mbox.setFont(self.font)
            mbox.setStyleSheet(self.sheetstyle)
            mbox.exec()
            return
        self.submitClicked.emit(txt)
        self.close()


def launch_add_user(existing_users):
    app = QtWidgets.QApplication(sys.argv)
    win = AddUser(existing_users)
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    existing_users = ['test@test']
    launch_add_user(existing_users)
    print(f'{existing_users=}')
