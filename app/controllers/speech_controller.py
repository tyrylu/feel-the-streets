from PySide6.QtWidgets import QApplication
from ..services import speech, menu_service
from ..menu_service import menu_command

class SpeechController:
    def __init__(self):
        menu_service().register_menu_commands(self)

    @menu_command(_("Speech"), _("Silence"), "s")
    def silence_speech(self, evt):
        speech().silence()

    @menu_command(_("Speech"), _("Move to and speak the first speech history item"), "home")
    def move_and_speak_first(self):
        if speech().move_to_first_history_item():
            speech().speak_current_history_item()
        else:
            speech().speak(_("Already on the first history item."), add_to_history=False)

    @menu_command(_("Speech"), _("Move to and speak the previous speech history item"), "page up")
    def move_and_speak_previous(self):
        if speech().move_to_previous_history_item():
            speech().speak_current_history_item()
        else:
            speech().speak(_("Already on the first history item."), add_to_history=False)

    @menu_command(_("Speech"), _("Move to and speak the next speech history item"), "page down")
    def move_and_speak_next(self):
        if speech().move_to_next_history_item():
            speech().speak_current_history_item()
        else:
            speech().speak(_("Already on the last history item."), add_to_history=False)

    @menu_command(_("Speech"), _("Move to and speak the last speech history item"), "end")
    def move_and_speak_last(self):
        if speech().move_to_last_history_item():
            speech().speak_current_history_item()
        else:
            speech().speak(_("Already on the last history item."), add_to_history=False)

    @menu_command(_("Speech"), _("Copy current speech history item to the clipboard"), "ctrl+c")
    def copy_current_item(self):
        QApplication.clipboard().setText(speech().current_history_item)
        speech().speak(_("Copied."), interrupt=True, add_to_history=False)

    @menu_command(_("Speech"), _("Repeat the current speech history item"), "del")
    def repeat_history_item(self):
        speech().speak_current_history_item()