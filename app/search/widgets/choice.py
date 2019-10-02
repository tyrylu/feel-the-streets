import wx
from osm_db import Enum
from . import widget_for
from shared.humanization_utils import underscored_to_words

@widget_for("Enum")
class Choice:

    value_label = _("Value")
    @staticmethod
    def get_value_widget(parent, column):
        choice = wx.Choice(parent)
        enum = Enum.with_name(column.type_name)
        name = enum.name_for_value(0)
        index = 1
        while name:
            choice.Append(underscored_to_words(name))
            index += 1
            name = enum.name_for_value(index)
        return choice

    @staticmethod
    def get_value_as_string(value_widget):
        return value_widget.GetString(value_widget.CurrentSelection)
    
    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.Selection