import os
import sys
import gettext
import logging
import locale
from PySide2.QtCore import QTranslator, QLocale
from PySide2.QtWidgets import QApplication

log = logging.getLogger(__name__)

def setup_locale():
    """Setups the locale machinery."""
    root_dir = os.path.join(os.path.dirname(sys.argv[0]))
    locales_dir = os.path.join(root_dir, "locale")
    # The gettext support requires the LANG environment variable even on win32.
    if sys.platform == "win32" and "LANG" not in os.environ:
        lang, enc = locale.getdefaultlocale()
        os.environ["LANG"] = lang
    locale.setlocale(locale.LC_ALL, "")
    gettext.install("messages", locales_dir)
    translator = QTranslator(QApplication.instance())
    if not translator.load(QLocale.system(), "qtbase_", directory=locales_dir):
        log.warning("Failed to load the QT locale data.")
    if not QApplication.instance().installTranslator(translator):
        log.warning("Failed to install the QT translator.")

