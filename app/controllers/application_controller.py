from PySide2.QtWidgets import QApplication
from ..services import menu_service, speech
from ..menu_service import menu_command
from ..area_selection import AreaSelectionDialog


class ApplicationController:
    def __init__(self, window):
        self._main_window = window
        menu_service().register_menu_commands(self)
    
    @menu_command(_("Program"), _("Select an area..."), None)
    def do_select_area(self):
        self._main_window.do_select_db(False)



    @menu_command(_("Program"), _("Quit"), "ctrl+q")
    def do_quit(self, evt):
        self._main_window.close()
        QApplication.instance().quit()