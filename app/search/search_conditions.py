import wx
from osm_db import EntityMetadata, FieldNamed
from shared.humanization_utils import underscored_to_words, get_class_display_name
from .operators import operators_for_column_class

class SpecifySearchConditionsDialog(wx.Dialog):
    xrc_name = "specify_search_conditions"
    
    def post_init(self, entity):
        self._entity = entity
        self._fields = self.FindWindowByName("fields")
        self._value_widget = None
        self._value_label = None
        self._search_expression_parts = []
        self._operator = self.FindWindowByName("operator")
        self._conditions = self.FindWindowByName("conditions")
        self._populate_fields_tree(self._entity)

    def _populate_fields_tree(self, entity, parent=None):
        if parent is None:
            parent = self._fields.AddRoot("Never to be seen")
        metadata = EntityMetadata.for_discriminator(entity)
        for field_name, field in sorted(metadata.all_fields.items(), key=lambda i: underscored_to_words(i[0])):
            child_metadata = None
            try:
                child_metadata = EntityMetadata.for_discriminator(field.type_name)
            except KeyError: pass
            if child_metadata:
                name = get_class_display_name(field.type_name)
                subparent = self._fields.AppendItem(parent, name)
                self._fields.SetItemData(subparent, field_name)
                self._populate_fields_tree(field.type_name, subparent)
            else:
                item = self._fields.AppendItem(parent, underscored_to_words(field_name))
                self._fields.SetItemData(item, (field_name, field))

    def on_fields_tree_sel_changed(self, evt):
        data = self._fields.GetItemData(evt.Item)
        if data is not None and not isinstance(data, str):
            self._field_name = data[0]
            self._field = data[1]
            self._operators = operators_for_column_class(self._field.type_name)
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
        value_label = self._create_value_label(operator.get_value_label(self._field))
        self._value_widget = operator.get_value_widget(main_panel, self._field)
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
        json_path = []
        parent_data = None
        try:
            parent_data = self._fields.GetItemData(self._fields.GetItemParent(self._fields.Selection))
        except wx.wxAssertionError:
            pass # Failed to retrieve the virtual root item, but that's okay, it just means that we don't need to add a relationship join.
        if isinstance(parent_data, str):
            json_path.append(parent_data)
        json_path.append(self._field_name)
        json_path = ".".join(json_path)
        operator_obj = self._operators[self._operator.Selection]
        expression = operator_obj.get_comparison_expression(self._field, FieldNamed(json_path), self._value_widget)
        self._search_expression_parts.append(expression)
        self._conditions.Append(f"{underscored_to_words(self._field_name)} {operator_obj.label} {operator_obj.get_value_as_string(self._field, self._value_widget)}")

    @property
    def distance(self):
        return self.FindWindowByName("distance").Value

    def create_conditions(self):
        conditions = []
        if self._search_expression_parts:
            for part in self._search_expression_parts:
                conditions.append(part)
        return conditions
        
       
    def on_remove_clicked(self, evt):   
        selection = self._conditions.Selection
        if selection < 0:
            return
        del self._search_expression_parts[selection]
        self._conditions.Delete(selection)
