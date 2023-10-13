"""
created matt_dumont
on: 7/10/23
"""
import datetime
import sys
from PyQt6 import QtGui, QtWidgets


class AuthUser(QtWidgets.QMainWindow):  # todo update simiar to add_user_gui.py
    saved = False

    def __init__(self, user_):
        assert isinstance(user_, str)
        assert type(user_) == str
        assert '@' in user_
        assert user_.islower()
        self.user = user_

        QtWidgets.QMainWindow.__init__(self)
        self.resize(200, 150)
        # frame box
        vert = QtWidgets.QVBoxLayout()

        # set font stats
        self.font = QtGui.QFont()
        self.sheetstyle = f"color: black; "

        label = QtWidgets.QLabel('User Email Address')
        label.setFont(self.font)
        label.setStyleSheet(self.sheetstyle)
        vert.addWidget(label)
        label = QtWidgets.QLabel(self.user)
        label.setFont(self.font)
        label.setStyleSheet(self.sheetstyle)
        vert.addWidget(label)
        self.answers = QtWidgets.QLineEdit('')
        self.answers.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        vert.addWidget(self.answers)
        # save/cancel buttons
        save = QtWidgets.QPushButton('Authenticate')
        save.clicked.connect(self.save)
        cancel = QtWidgets.QPushButton('Cancel')
        cancel.clicked.connect(self.close)
        horiz = QtWidgets.QHBoxLayout()
        horiz.addWidget(save)
        horiz.addWidget(cancel)
        vert.addLayout(horiz)
        w = QtWidgets.QWidget()
        w.setLayout(vert)
        self.setCentralWidget(w)

    def save(self):

        # todo how are you supposed to pass this... and how store/use safely... goes to
        # todo how does google oauth work?  how does it store the token?  how does it use it?
        raise NotImplementedError

        self.close()


def launch_auth_user(user_):
    app = QtWidgets.QApplication(sys.argv)
    win = AuthUser(user_)
    win.show()
    sys.exit(app.exec())

# todo security here!!!!

if __name__ == '__main__':
    user = 'test@test'
    launch_auth_user(user)
