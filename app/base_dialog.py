from PySide6.QtWidgets import QDialog, QPushButton, QGridLayout

class BaseDialog(QDialog):
    def __init__(self, parent, title, ok_text, cancel_text, ok_button_column=0, cancel_button_column=1, buttons_to_new_row=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.create_ui()
        buttons_row = self.layout.rowCount() if not buttons_to_new_row else self.layout.rowCount() + 1
        ok_button = QPushButton(ok_text, self)
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.ok_clicked)
        self.layout.addWidget(ok_button, buttons_row, ok_button_column)
        cancel_button = QPushButton(cancel_text, self)
        cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(cancel_button, buttons_row, cancel_button_column)


    def ok_clicked(self):
        self.accept()