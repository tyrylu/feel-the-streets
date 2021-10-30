from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel

class SearchIndicator(QWidget):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle(_("Search in progress"))
        self.setWindowModality(Qt.ApplicationModal)
        label = QLabel(_("The search is in progress, please wait..."), self)