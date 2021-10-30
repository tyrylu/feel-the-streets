from PySide6.QtWidgets import QCheckBox
from . import widget_for

@widget_for("bool")
class CheckBoxWidget:

    value_label = ""
    @staticmethod
    def get_value_widget(parent, column):
        return QCheckBox(_("Value"), parent)

    @staticmethod
    def get_value_as_string(value_widget):
        return str(value_widget.isChecked())

    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.isChecked()