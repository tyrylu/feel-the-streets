from .base_dialog import BaseDialog
from PySide6.QtWidgets import QTextBrowser, QLabel
from PySide6.QtCore import Qt

class MessageDialog(BaseDialog):

    def __init__(self, parent, motd):
        self._motd = motd
        super().__init__(parent, _("Message from the developer"), _("&Continue"), _("&Exit"))

    def create_ui(self):
        label = QLabel(_("The developer sent a message on {}").format(self._motd.timestamp_string))
        browser = QTextBrowser(self)
        label.setBuddy(browser)
        self.layout.addWidget(label, 0, 0, 1, 2)
        self.layout.addWidget(browser, 1, 0, 1, 2)
        browser.setTextInteractionFlags(Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse|Qt.LinksAccessibleByKeyboard|Qt.LinksAccessibleByMouse)
        browser.setOpenExternalLinks(True)
        browser.setMarkdown(self._motd.message)
        browser.setFocus()