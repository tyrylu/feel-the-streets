from . import operator_for
from .operator import Operator

@operator_for("DimensionalFloat", "Float", "Integer")
class GreaterThan(Operator):
    label = "Je větší než"

    @classmethod
    def get_comparison_expression(cls, column, value_widget):
        return column > cls.get_value_for_query(column, value_widget)