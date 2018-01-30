import wx
from . import widget_for

@widget_for("UnicodeText", "String")
class TextCtrl:

    value_label = "Hodnota"
    @staticmethod
    def get_value_widget(parent, column):
        return wx.TextCtrl(parent)

    @staticmethod
    def get_value_as_string(value_widget):
        return value_widget.Value
    
    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.Value