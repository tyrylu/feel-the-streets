from . import operator_for
from .operator import Operator

@operator_for("str")
class StartsWith(Operator):
    label = _("Starts with")

    @classmethod
    def get_comparison_expression(cls, field, value_expr, value_widget):
        return value_expr.like("{0}%".format(cls.get_value_for_query(field, value_widget)))