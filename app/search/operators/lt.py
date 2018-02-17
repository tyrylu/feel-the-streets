from . import operator_for
from .operator import Operator
from shared.validated_quantity import Quantity

@operator_for(Quantity, float, int)
class LessThan(Operator):
    label = _("Is less than")

    @classmethod
    def get_comparison_expression(cls, field, value_expr, value_widget):
        return value_expr < cls.get_value_for_query(field, value_widget)