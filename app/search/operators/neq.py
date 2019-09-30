from . import operator_for
from .operator import Operator

@operator_for("*", priority=-1)
class NotEquals(Operator):
    label = _("Is not equal")

    @classmethod
    def get_comparison_expression(cls, value_expr, field, value_widget):
        return value_expr.neq(cls.get_value_for_query(field, value_widget))