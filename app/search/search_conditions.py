import wx
from shared.model_introspection import all_model_columns, get_column_display_name, get_related_class, get_foreign_display_name, get_relationship_of
from .operators import operators_for_column_class
from ..services import map

class SpecifySearchConditionsDialog(wx.Dialog):
    xrc_name = "specify_search_conditions"
    
    def post_init(self, model):
        self._model = model
        self._fields = self.FindWindowByName("fields")
        self._value_widget = None
        self._value_label = None
        self._search_expression_parts = []
        self._join_table_mapping = {}
        self._needed_joins = []
        self._operator = self.FindWindowByName("operator")
        self._conditions = self.FindWindowByName("conditions")
        self._populate_fields_tree(self._model)

    def _populate_fields_tree(self, entity, parent=None):
        if parent is None:
            parent = self._fields.AddRoot("Never to be seen")
        for column in all_model_columns(entity):
            if column.name.endswith("_id") and column.foreign_keys:
                related_class = get_related_class(entity, column)
                name = get_foreign_display_name(related_class)
                self._join_table_mapping[name] = get_relationship_of(entity, column)
                subparent = self._fields.AppendItem(parent, name)
                self._populate_fields_tree(related_class, subparent)
            else:
                item = self._fields.AppendItem(parent, get_column_display_name(column))
                self._fields.SetItemData(item, column)

    def on_fields_tree_sel_changed(self, evt):
        self._column = self._fields.GetItemData(evt.Item)
        if self._column is not None:
            self._operators = operators_for_column_class(self._column.type.__class__.__name__)
            self._operator.Clear()
            for operator in self._operators:
                self._operator.Append(operator.label)

    def on_operator_choice(self, evt):
        if self._value_widget:
            self._value_widget.Destroy()
        if self._value_label:
            self._value_label.Destroy()
        operator = self._operators[self._operator.Selection]
        main_panel = self.FindWindowByName("main_panel")
        # The label *must* be created first, because there is no way how to set the label text as the accessible name of the operator widget afterwards.
        value_label = self._create_value_label(operator.get_value_label(self._column))
        self._value_widget = operator.get_value_widget(main_panel, self._column)
        if not self._value_widget:
            return
        self._value_widget.MoveAfterInTabOrder(self._operator)
        panel_sizer = main_panel.Sizer
        self._value_label = value_label
        if self._value_label:
            panel_sizer.Add(self._value_label, (0, 2))
        panel_sizer.Add(self._value_widget, (1, 2))
        panel_sizer.Layout()
        self.Fit()

    def _create_value_label(self, label):
        if not label:
            return
        panel = self.FindWindowByName("main_panel")
        label = wx.StaticText(panel, label=label)
        return label

    def on_add_clicked(self, evt):
        operator_obj = self._operators[self._operator.Selection]
        expression = operator_obj.get_comparison_expression(self._column, self._value_widget)
        self._search_expression_parts.append(expression)
        parent_text = None
        try:
            parent_text = self._fields.GetItemText(self._fields.GetItemParent(self._fields.Selection))
        except wx.wxAssertionError:
            pass # Failed to retrieve the virtual root item, but that's okay, it just means that we don't need to add a relationship join.
        if parent_text in self._join_table_mapping:
            self._needed_joins.append(self._join_table_mapping[parent_text])
        self._conditions.Append(f"{get_column_display_name(self._column)} {operator_obj.label} {operator_obj.get_value_as_string(self._column, self._value_widget)}")

    @property
    def distance(self):
        return self.FindWindowByName("distance").Value

    def create_query(self):
        if self._search_expression_parts:
            conditions = self._search_expression_parts[0]
            for part in self._search_expression_parts[1:]:
                conditions = conditions & part
            query = map()._db.query(self._model)
            for joined_column in self._needed_joins:
                query = query.join(joined_column)
            query = query.filter(conditions)
            print(f"Result count: {query.count()}")
            return query


    def on_remove_clicked(self, evt):   
        selection = self._conditions.Selection
        if selection < 0:
            return
        del self._search_expression_parts[selection]
        self._conditions.Delete(selection)
