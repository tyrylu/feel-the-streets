from ..widgets import widget_for_column_class

class Operator:

    @staticmethod
    def get_value_widget(parent, column):
        return widget_for_column_class(column.type_).get_value_widget(parent, column)

    @staticmethod
    def get_value_as_string(column, value_widget):
        return widget_for_column_class(column.type_).get_value_as_string(value_widget)

    @staticmethod
    def get_value_label(column):
        return widget_for_column_class(column.type_).value_label

    @staticmethod
    def get_value_for_query(column, value_widget):
        return widget_for_column_class(column.type_).get_value_for_query(column, value_widget)