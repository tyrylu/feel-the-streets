import os
import sys
import wx
import builtins

def setup_locale():
    """Locale setup, including the __builtins__ hack similar to the gettext.install's one."""
    locale = wx.Locale(wx.LANGUAGE_DEFAULT)
    locale.AddCatalogLookupPathPrefix(os.path.join(os.path.dirname(sys.argv[0]), "locale"))
    locale.AddCatalog("messages")
    builtins.__dict__['_'] = locale.GetString