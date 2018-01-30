from . import operator_for
from .operator import Operator

@operator_for("*", priority=-1)
class Equals(Operator):
    label = "Je rovno"

    @classmethod
    def get_comparison_expression(cls, column, value_widget):
        return column == cls.get_value_for_query(column, value_widget)