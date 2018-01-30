from ..uimanager import get, menu_command


class ApplicationController:
    def __init__(self, window):
        self._main_window = window
        get().register_menu_commands(self)
    @menu_command("Program", "Konec", "ctrl+q")
    def do_quit(self, evt):
        self._main_window.Destroy()