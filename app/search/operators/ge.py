from . import operator_for
from .operator import Operator

@operator_for("Quantity", "float", "int")
class GreaterThanOrEqual(Operator):
    label = _("Is greater than or equal")

    @classmethod
    def get_comparison_expression(cls, field, value_expr, value_widget):
        return value_expr.ge(cls.get_value_for_query(field, value_widget))