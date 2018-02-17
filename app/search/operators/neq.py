from . import operator_for
from .operator import Operator

@operator_for("*", priority=-1)
class NotEquals(Operator):
    label = _("Is not equal")

    @classmethod
    def get_comparison_expression(cls, field, value_expr, value_widget):
        return column != cls.get_value_for_query(column, value_widget)