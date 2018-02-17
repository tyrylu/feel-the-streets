import wx
from . import widget_for

@widget_for(bool)
class CheckBoxWidget:

    value_label = ""
    @staticmethod
    def get_value_widget(parent, column):
        return wx.CheckBox(parent, label=_("Value"))

    @staticmethod
    def get_value_as_string(value_widget):
        return value_widget.Value

    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.Value