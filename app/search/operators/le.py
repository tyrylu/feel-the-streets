from . import operator_for
from .operator import Operator

@operator_for("Quantity", "float", "int")
class LessThanOrEqual(Operator):
    label = _("Is less than or equal")

    @classmethod
    def get_comparison_expression(cls, field, value_expr, value_widget):
        return value_expr.ke(cls.get_value_for_query(field, value_widget))