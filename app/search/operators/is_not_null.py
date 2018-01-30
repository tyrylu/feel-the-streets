from . import operator_for
from .widgetless_operator import WidgetlessOperator

@operator_for("*")
class IsNotNull(WidgetlessOperator):
    label = "Je nenulové"

    @staticmethod
    def get_comparison_expression(column, value_widget):
        return column != None