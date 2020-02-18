from PySide2.QtWidgets import QLineEdit
from . import widget_for

@widget_for("str")
class TextCtrl:

    value_label = _("Value")
    @staticmethod
    def get_value_widget(parent, column):
        return QLineEdit(parent)

    @staticmethod
    def get_value_as_string(value_widget):
        return value_widget.text()
    
    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.text()