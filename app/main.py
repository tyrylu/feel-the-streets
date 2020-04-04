import sys
import os
import logging
from PySide2.QtWidgets import QApplication
import osm_db
from . import locale_setup

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
    ret = app.exec_()
    sys.exit(ret)



if __name__ == "__main__":
    main()