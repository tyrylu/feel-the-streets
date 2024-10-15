from PySide6.QtCore import qVersion
if qVersion() >= "6.8":
    available = True
    from PySide6.QtGui import QGuiApplication, QAccessible, QAccessibleAnnouncementEvent
else:
    available = False

class Output:
    def __init__(self):
        self._parent = QGuiApplication.instance()

    def speak(self, text, interrupt):
        if available:
            event = QAccessibleAnnouncementEvent(self._parent, text)
            politeness = QAccessible.AnnouncementPoliteness.Assertive if interrupt else QAccessible.AnnouncementPoliteness.Polite
            event.setPoliteness(politeness)
            QAccessible.updateAccessibility(event)

    def get_first_available_output(self):
        return None
