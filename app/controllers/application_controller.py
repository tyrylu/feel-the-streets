from ..services import menu_service
from ..menu_service import menu_command

class ApplicationController:
    def __init__(self, window):
        self._main_window = window
        menu_service().register_menu_commands(self)
    
    @menu_command(_("Program"), _("Quit"), "ctrl+q")
    def do_quit(self, evt):
        self._main_window.close()