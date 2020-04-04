from . import operator_for
from .widgetless_operator import WidgetlessOperator

@operator_for("*")
class IsNotNull(WidgetlessOperator):
    label = _("Is not null")

    @staticmethod
    def get_comparison_expression(field, value_expr, value_widget):
        return value_expr.is_not_null()