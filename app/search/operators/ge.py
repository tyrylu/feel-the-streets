from . import operator_for
from shared.validated_quantity import Quantity
from .operator import Operator

@operator_for(Quantity, float, int)
class GreaterThanOrEqual(Operator):
    label = "Je větší nebo rovno než"

    @classmethod
    def get_comparison_expression(cls, field, value_expr, value_widget):
        return value_expr >= cls.get_value_for_query(field, value_widget)