import wx
from shared.validated_quantity import Quantity
from . import widget_for

widget_for(float, Quantity)
class SpinCtrlDouble:

    value_label = "Hodnota"
    @staticmethod
    def get_value_widget(parent, column):
        return wx.SpinCtrlDouble(parent, min=float("-inf"), max=float("inf"))

    @staticmethod
    def get_value_as_string(value_widget):
        return value_widget.Value
    
    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.Value