"""
created matt_dumont 
on: 17/10/23
"""
import sys
from PyQt6 import QtGui, QtWidgets, QtCore


class AddRmDrives(QtWidgets.QWidget):
    submitClicked = QtCore.pyqtSignal(list)

    def __init__(self, user, current_drives, available_drives):
        super().__init__()
        self.user = user
        lay = self.setup_layout()
        self.InactiveDrives.addItems(available_drives)
        self.ActiveDrives.addItems(current_drives)
        self.setLayout(lay)
        self.show()

    def _set_fonts(self):
        self.font_bold = QtGui.QFont()
        self.font_bold.setBold(True)
        self.font_plain = QtGui.QFont()
        self.font_plain.setBold(False)
        self.sheetstyle = f"color: black; "

    def setup_layout(self):
        self._set_fonts()
        total_lay = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel(f'Select Drives to Add/Remove for {self.user}')
        label.setFont(self.font_bold)
        label.setStyleSheet(self.sheetstyle)
        total_lay.addWidget(label)

        lay = QtWidgets.QHBoxLayout()

        self.InactiveDrives = QtWidgets.QListWidget()
        self.InactiveDrives.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.ActiveDrives = QtWidgets.QListWidget()
        self.ActiveDrives.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

        self.mButtonToSelected = QtWidgets.QPushButton(">>")
        self.mBtnMoveToAvailable = QtWidgets.QPushButton(">")
        self.mBtnMoveToSelected = QtWidgets.QPushButton("<")
        self.mButtonToAvailable = QtWidgets.QPushButton("<<")

        self.inactive_layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel('Inactive Drives')
        label.setFont(self.font_bold)
        label.setStyleSheet(self.sheetstyle)
        self.inactive_layout.addWidget(label)
        hlay0 = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Search:')
        label.setFont(self.font_plain)
        label.setStyleSheet(self.sheetstyle)
        self.inactive_search = QtWidgets.QLineEdit()
        self.inactive_search.textChanged.connect(self.search_item_inactive)
        hlay0.addWidget(label)
        hlay0.addWidget(self.inactive_search)
        self.inactive_layout.addLayout(hlay0)
        self.inactive_layout.addWidget(self.InactiveDrives)

        self.active_layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('Active Drives')
        label.setFont(self.font_bold)
        label.setStyleSheet(self.sheetstyle)
        self.active_layout.addWidget(label)
        hlay0 = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Search:')
        label.setFont(self.font_plain)
        label.setStyleSheet(self.sheetstyle)
        self.active_search = QtWidgets.QLineEdit()
        self.active_search.textChanged.connect(self.search_item_active)
        hlay0.addWidget(label)
        hlay0.addWidget(self.active_search)
        self.active_layout.addLayout(hlay0)
        self.active_layout.addWidget(self.ActiveDrives)

        vlay = QtWidgets.QVBoxLayout()
        vlay.addStretch()
        vlay.addWidget(self.mButtonToSelected)
        vlay.addWidget(self.mBtnMoveToAvailable)
        vlay.addWidget(self.mBtnMoveToSelected)
        vlay.addWidget(self.mButtonToAvailable)
        vlay.addStretch()

        vlay2 = QtWidgets.QVBoxLayout()
        vlay2.addStretch()
        vlay2.addStretch()

        lay.addLayout(self.inactive_layout)
        lay.addLayout(vlay)
        lay.addLayout(self.active_layout)
        lay.addLayout(vlay2)

        total_lay.addLayout(lay)
        submit_btn = QtWidgets.QPushButton('Submit')
        submit_btn.clicked.connect(self.done)
        quit_btn = QtWidgets.QPushButton('Cancel')
        quit_btn.clicked.connect(self.cancel)
        hlay = QtWidgets.QHBoxLayout()
        hlay.addStretch()
        hlay.addWidget(submit_btn)
        hlay.addStretch()
        hlay.addWidget(quit_btn)
        hlay.addStretch()

        total_lay.addLayout(hlay)

        self.update_buttons_status()
        self.connections()
        return total_lay

    def search_item_active(self):
        self.search_item(self.active_search.text(), self.ActiveDrives)

    def search_item_inactive(self):
        self.search_item(self.inactive_search.text(), self.InactiveDrives)

    def search_item(self, search_string, list_widget):
        match_items = list_widget.findItems(search_string, QtCore.Qt.MatchFlag.MatchContains)
        for i in range(list_widget.count()):
            it = list_widget.item(i)
            it.setHidden(it not in match_items)

    @QtCore.pyqtSlot()
    def update_buttons_status(self):
        self.mBtnMoveToAvailable.setDisabled(
            not bool(self.InactiveDrives.selectedItems()) or self.ActiveDrives.currentRow() == 0)
        self.mBtnMoveToSelected.setDisabled(not bool(self.ActiveDrives.selectedItems()))

    def connections(self):
        self.InactiveDrives.itemSelectionChanged.connect(self.update_buttons_status)
        self.ActiveDrives.itemSelectionChanged.connect(self.update_buttons_status)
        self.mBtnMoveToAvailable.clicked.connect(self.on_mBtnMoveToAvailable_clicked)
        self.mBtnMoveToSelected.clicked.connect(self.on_mBtnMoveToSelected_clicked)
        self.mButtonToAvailable.clicked.connect(self.on_mButtonToAvailable_clicked)
        self.mButtonToSelected.clicked.connect(self.on_mButtonToSelected_clicked)

    @QtCore.pyqtSlot()
    def on_mBtnMoveToAvailable_clicked(self):
        change_items = self.InactiveDrives.selectedItems()
        for item in change_items:
            self.ActiveDrives.addItem(
                self.InactiveDrives.takeItem(self.InactiveDrives.row(item)))

    @QtCore.pyqtSlot()
    def on_mBtnMoveToSelected_clicked(self):
        change_items = self.ActiveDrives.selectedItems()
        for item in change_items:
            self.InactiveDrives.addItem(
                self.ActiveDrives.takeItem(self.ActiveDrives.row(item)))

    @QtCore.pyqtSlot()
    def on_mButtonToAvailable_clicked(self):
        while self.ActiveDrives.count() > 0:
            self.InactiveDrives.addItem(self.ActiveDrives.takeItem(0))

    @QtCore.pyqtSlot()
    def on_mButtonToSelected_clicked(self):
        while self.InactiveDrives.count() > 0:
            self.ActiveDrives.addItem(self.InactiveDrives.takeItem(0))

    @QtCore.pyqtSlot()
    def on_mBtnUp_clicked(self):
        row = self.ActiveDrives.currentRow()
        currentItem = self.ActiveDrives.takeItem(row)
        self.ActiveDrives.insertItem(row - 1, currentItem)
        self.ActiveDrives.setCurrentRow(row - 1)

    @QtCore.pyqtSlot()
    def on_mBtnDown_clicked(self):
        row = self.ActiveDrives.currentRow()
        currentItem = self.ActiveDrives.takeItem(row)
        self.ActiveDrives.insertItem(row + 1, currentItem)
        self.ActiveDrives.setCurrentRow(row + 1)

    def get_inactive_elements(self):
        r = []
        for i in range(self.InactiveDrives.count()):
            it = self.InactiveDrives.item(i)
            r.append(it.text())
        return r

    def get_get_active_elements(self):
        r = []
        for i in range(self.ActiveDrives.count()):
            it = self.ActiveDrives.item(i)
            r.append(it.text())
        return r

    def cancel(self):
        self.submitClicked.emit([self.user, None])
        self.close()

    def done(self):
        self.submitClicked.emit([self.user] + self.get_get_active_elements())
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    w = AddRmDrives('test@test.com', ['asadf', 'basfd', 'casdf'], ['dasdf', 'esasfg', 'fasdf'])

    w.show()
    sys.exit(app.exec())
