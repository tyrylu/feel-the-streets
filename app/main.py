import sys
import os
import threading
import logging
import webbrowser
from PySide6.QtWidgets import QApplication, QMessageBox
import osm_db
from . import locale_setup
from .services import speech, config

log = logging.getLogger(__name__)

def handle_error(exc, thread=None):
    if not QApplication.instance():
        _app = QApplication()
    if not thread:
        log.exception("Unhandled exception in main thread", exc_info=exc)
    else:
        log.exception("Unhandled exception in thread %s", thread, exc_info=exc)
    resp = QMessageBox.critical(None, _("Unexpected error"), _("The application encountered an unexpected error, please contact the developer and provide the contents of fts.log which is located in the folder with the executable. Do you want to see it now?"), QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
    if resp == QMessageBox.StandardButton.Yes:
        webbrowser.open("fts.log")

    sys.exit(1)

def main():
    threading.excepthook = lambda args: handle_error(args.exc_value, args.thread)
    sys.excepthook = lambda type, value, traceback: handle_error(value)
    # Teach python about the trace level used by the rust extension
    logging.addLevelName(5, "TRACE")
    level = os.environ.get("FTS_LOG", "info")
    logging.basicConfig(level=logging._nameToLevel[level.upper()], filename="fts.log", filemode="w")
    osm_db.init_logging(level)
    # We need the QT application before setting up the locale stuff...
    app = QApplication(sys.argv)
    locale_setup.setup_locale(config().general.language)
    # Now we can import the application window - we have the translation function.
    from .main_window import MainWindow
    mw = MainWindow()
    # If we don't show the main window early enough, the event loop can exit prematurely in some cases.
    mw.show()
    ret = app.exec_()
    # On Linux, the speech dispatcher communication thread is still running and it's a daemon one, so using sys.exit now would not have any effect.
    # To workaround that, destroy the speech instance and let the destructor take care of the things it needs
    speech.reset()
    sys.exit(ret)



if __name__ == "__main__":
    main()