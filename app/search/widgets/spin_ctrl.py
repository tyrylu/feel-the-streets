import wx
from . import widget_for

@widget_for(int)
class SpinCtrl:
    value_label = _("Value")

    @staticmethod
    def get_value_widget(parent, column):
        return wx.SpinCtrl(parent, max=2**30, min=-(2**30))

    @staticmethod
    def get_value_as_string(value_widget):
        return value_widget.Value

    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.Value