from . import operator_for
from .widgetless_operator import WidgetlessOperator

@operator_for("*")
class IsNull(WidgetlessOperator):
    label = _("Is null")

    @staticmethod
    def get_comparison_expression(_field, value_expr, _value_widget):
        return value_expr.is_null()