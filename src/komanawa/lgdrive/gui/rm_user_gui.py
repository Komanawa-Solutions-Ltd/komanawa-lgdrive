"""
created matt_dumont 
on: 17/10/23
"""

from PyQt6 import QtGui, QtWidgets, QtCore
from komanawa.lgdrive.path_support import icon_path
class RmUser(QtWidgets.QWidget):
    submitClicked = QtCore.pyqtSignal(list)

    def __init__(self, user):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.setWindowTitle('Google Path support')
        # frame box
        self.user = user
        vert = QtWidgets.QVBoxLayout()
        lab = QtWidgets.QLabel(f'Are you sure you want to remove\n{user}?')
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.sheetstyle = f"color: black; "
        lab.setFont(self.font)
        lab.setStyleSheet(self.sheetstyle)

        vert.addWidget(lab)
        # save/cancel buttons
        save = QtWidgets.QPushButton(f'Remove {user}')
        save.clicked.connect(self.remove_user)
        cancel = QtWidgets.QPushButton('Cancel')
        cancel.clicked.connect(self.quit)
        horiz = QtWidgets.QHBoxLayout()
        horiz.addWidget(save)
        horiz.addWidget(cancel)
        vert.addLayout(horiz)
        self.setLayout(vert)
        self.show()
    def remove_user(self):
        self.submitClicked.emit([True, self.user])
        self.close()

    def quit(self):
        self.submitClicked.emit([False, self.user])
        self.close()

class ReAuthUser(QtWidgets.QWidget):
    submitClicked = QtCore.pyqtSignal(list)

    def __init__(self, user, authenticated):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.setWindowTitle('Google Path support')
        # frame box
        self.user = user
        vert = QtWidgets.QVBoxLayout()
        if authenticated:
            lab = QtWidgets.QLabel(f'Are you sure you want to re-authenticate\n{user}?')
        else:
            lab = QtWidgets.QLabel(f'Are you sure you want to authenticate\n{user}?')
        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.sheetstyle = f"color: black; "
        lab.setFont(self.font)
        lab.setStyleSheet(self.sheetstyle)

        vert.addWidget(lab)
        # save/cancel buttons
        save = QtWidgets.QPushButton(f'Authenticate {user}')
        save.clicked.connect(self.aut_user)
        cancel = QtWidgets.QPushButton('Cancel')
        cancel.clicked.connect(self.quit)
        horiz = QtWidgets.QHBoxLayout()
        horiz.addWidget(save)
        horiz.addWidget(cancel)
        vert.addLayout(horiz)
        self.setLayout(vert)
        self.show()
    def aut_user(self):
        self.submitClicked.emit([True, self.user])
        self.close()

    def quit(self):
        self.submitClicked.emit([False, self.user])
        self.close()



if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = RmUser('test@test')
    win.show()
    sys.exit(app.exec())