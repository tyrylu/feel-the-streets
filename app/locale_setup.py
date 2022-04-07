import os
import sys
import gettext
import logging
import locale
from PySide6.QtCore import QTranslator, QLocale
from PySide6.QtWidgets import QApplication

log = logging.getLogger(__name__)

def setup_locale(lang):
    """Setups the locale machinery for the specified language or the system default."""
    root_dir = os.path.join(os.path.dirname(sys.argv[0]))
    locales_dir = os.path.join(root_dir, "locale")
    # First, set the language for gettext and friends if it is not a system default
    if lang != "system":
        os.environ["LANG"] = lang
    # The gettext support requires the LANG environment variable even on win32.
    if lang == "system" and sys.platform == "win32" and "LANG" not in os.environ:
        lang, _enc = locale.getdefaultlocale()
        os.environ["LANG"] = lang
    locale.setlocale(locale.LC_ALL, "")
    gettext.install("messages", locales_dir)
    translator = QTranslator(QApplication.instance())
    if lang == "system":
        qt_locale = QLocale.system()
    else:
        qt_locale = QLocale(lang)
    if not translator.load(qt_locale, "qtbase_", directory=locales_dir):
        log.warning("Failed to load the QT locale data.")
    if not QApplication.instance().installTranslator(translator):
        log.warning("Failed to install the QT translator.")

