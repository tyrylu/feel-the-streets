from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel

class SearchIndicator(QWidget):
    def __init__(self, parent):
        super().__init__(None)
        self.setWindowTitle(_("Search in progress"))
        self.setWindowModality(Qt.ApplicationModal)
        label = QLabel(_("The search is in progress, please wait..."), self)