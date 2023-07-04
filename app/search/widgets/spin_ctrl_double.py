from PySide6.QtWidgets import QDoubleSpinBox 
from . import widget_for

widget_for("float", "Quantity")
class SpinCtrlDouble:

    value_label = _("Value")
    @staticmethod
    def get_value_widget(parent, column):
        box = QDoubleSpinBox(parent)
        box.setMinimum(float("-inf"))
        box.setMaximum(float("inf"))
        return box

    @staticmethod
    def get_value_as_string(value_widget):
        return value_widget.value()
    
    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.value()