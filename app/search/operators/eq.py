from . import operator_for
from .operator import Operator

@operator_for("*", priority=-1)
class Equals(Operator):
    label = _("Equals")

    @classmethod
    def get_comparison_expression(cls, field, value_expr, value_widget):
        return value_expr.eq(cls.get_value_for_query(field, value_widget))