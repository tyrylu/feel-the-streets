import sys
import os
import logging
from PySide2.QtWidgets import QApplication
import osm_db
from . import locale_setup
from .services import speech

def main():
    level = logging._nameToLevel[os.environ.get("FTS_LOG", "info").upper()]
    logging.basicConfig(level=level)
    osm_db.init_logging()
    # We need the QT application before setting up the locale stuff...
    app = QApplication(sys.argv)
    locale_setup.setup_locale()
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