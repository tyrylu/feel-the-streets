from enum import Enum
import wx
from . import widget_for
from shared.humanization_utils import underscored_to_words

@widget_for(Enum)
class Choice:

    value_label = _("Value")
    @staticmethod
    def get_value_widget(parent, column):
        choice = wx.Choice(parent)
        for member in column.type_:
            choice.Append(underscored_to_words(member.name))
        return choice

    @staticmethod
    def get_value_as_string(value_widget):
        return value_widget.GetString(value_widget.CurrentSelection)
    
    @staticmethod
    def get_value_for_query(column, value_widget):
        return value_widget.Selection