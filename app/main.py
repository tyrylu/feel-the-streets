import sys
import os
import logging
import wx
import uimanager
from . import locale_setup

def main():
    logging.basicConfig(level=logging.INFO)
    app = wx.App()
    locale_setup.setup_locale()
    if getattr(sys, "frozen", False):
        ui_file = os.path.join(sys._MEIPASS, "ui.xrc")
    else:
        ui_file = os.path.join(os.path.dirname(__file__), "ui.xrc")
    # We must do the import so late that the locale setup is complete.
    from . import main_frame
    mgr = uimanager.UIManager(ui_file, "main_frame", reuse_app=True, load_on=main_frame.MainFrame())
    mgr.top_level.post_create()
    mgr.auto_bind(mgr.top_level, mgr.top_level)
    mgr.run()