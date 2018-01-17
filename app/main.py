import os
import logging
import wx
from . import main_frame
from . import uimanager

def main():
    #logging.basicConfig(level=logging.DEBUG)
    app = wx.App()
    ui_file = os.path.join(os.path.dirname(__file__), "ui.xrc")
    mgr = uimanager.UIManager(ui_file, "main_frame", reuse_app=True, load_on=main_frame.MainFrame())
    mgr.top_level.post_create()
    mgr.auto_bind(mgr.top_level, mgr.top_level)
    mgr.run()