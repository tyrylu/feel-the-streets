from . import operator_for
from .widgetless_operator import WidgetlessOperator

@operator_for("*")
class IsNull(WidgetlessOperator):
    label = "Je nulové"

    @staticmethod
    def get_comparison_expression(field, value_expr, value_widget):
        return value_expr == None