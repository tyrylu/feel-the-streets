from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPushButton, QLabel, QSpinBox, QTreeWidget, QTreeWidgetItem, QComboBox, QListWidget, QWidget
from osm_db import EntityMetadata, FieldNamed
from ..base_dialog import BaseDialog
from ..humanization_utils import underscored_to_words, get_class_display_name
from .operators import operators_for_column_class

class SpecifySearchConditionsDialog(BaseDialog):
    
    def __init__(self, parent, entity):
        super().__init__(parent, _("Search criteria"), _("&Start search"), _("&Cancel"))
        self._entity = entity
        self._value_widget = None
        self._value_label = None
        self._search_expression_parts = []
        self._populate_fields_tree(self._entity)

    def create_ui(self):
        fields_label = QLabel(_("Class fields"), self)
        self.layout.addWidget(fields_label, 0, 0)
        self._fields_tree = QTreeWidget(self)
        fields_label.setBuddy(self._fields_tree)
        self._fields_tree.currentItemChanged.connect(self.on_fields_tree_sel_changed)
        self.layout.addWidget(self._fields_tree, 1, 0)
        operator_label = QLabel(_("Operator"), self)
        self.layout.addWidget(operator_label, 0, 1)
        self._operator = QComboBox(self)
        operator_label.setBuddy(self._operator)
        self.layout.addWidget(self._operator, 1, 1)
        self._operator.currentIndexChanged.connect(self.on_operator_choice)
        self._operator.setCurrentIndex(0)
        add_button = QPushButton(_("&Add condition"), self)
        add_button.clicked.connect(self.on_add_clicked)
        self.layout.addWidget(add_button, 2, 0, 1, 3)
        criteria_label = QLabel(_("Current search criteria"), self)
        self.layout.addWidget(criteria_label, 3, 0, 1, 3)
        self._criteria_list = QListWidget(self)
        criteria_label.setBuddy(self._criteria_list)
        self.layout.addWidget(self._criteria_list, 4, 0, 1, 3)
        remove_button = QPushButton(_("&Remove condition"), self)
        remove_button.clicked.connect(self.on_remove_clicked)
        self.layout.addWidget(remove_button, 5, 0, 1, 3)
        distance_label = QLabel(_("Search objects to distance (in meters, 0 no limit)"), self)
        self.layout.addWidget(distance_label, 6, 0)
        self._distance_field = QSpinBox(self)
        distance_label.setBuddy(self._distance_field)
        self.layout.addWidget(self._distance_field, 6, 1)
        
    def _populate_fields_tree(self, entity, parent=None):
        if parent is None:
            parent = self._fields_tree.invisibleRootItem()
        metadata = EntityMetadata.for_discriminator(entity)
        for field_name, field in sorted(metadata.all_fields.items(), key=lambda i: underscored_to_words(i[0])):
            child_metadata = None
            try:
                child_metadata = EntityMetadata.for_discriminator(field.type_name)
            except KeyError: pass
            if child_metadata:
                name = get_class_display_name(field.type_name)
                subparent = QTreeWidgetItem([name])
                subparent.setData(0, Qt.UserRole, field_name)
                parent.addChild(subparent)
                self._populate_fields_tree(field.type_name, subparent)
            else:
                item = QTreeWidgetItem([underscored_to_words(field_name)])
                item.setData(0, Qt.UserRole, (field_name, field))
                parent.addChild(item)
                
    def on_fields_tree_sel_changed(self, item):
        data = item.data(0, Qt.UserRole)
        if data is not None and not isinstance(data, str):
            self._field_name = data[0]
            self._field = data[1]
            self._operators = operators_for_column_class(self._field.type_name)
            self._operator.clear()
            for operator in self._operators:
                self._operator.addItem(operator.label)

    def on_operator_choice(self, index):
        if self._value_widget:
            self.layout.removeWidget(self._value_widget)
            self._value_widget.deleteLater()
        if self._value_label:
            self.layout.removeWidget(self._value_label)
            self._value_label.deleteLater()
            self._value_label = None
        operator = self._operators[self._operator.currentIndex()]
        value_label = self._create_value_label(operator.get_value_label(self._field))
        self._value_widget = operator.get_value_widget(self, self._field)
        if not self._value_widget:
            return
        QWidget.setTabOrder(self._operator, self._value_widget)
        self._value_label = value_label
        if self._value_label:
            self._value_label.setBuddy(self._value_widget)
            self.layout.addWidget(self._value_label, 0, 2)
        self.layout.addWidget(self._value_widget, 1, 2)

    def _create_value_label(self, label):
        if not label:
            return
        label = QLabel(label, self)
        return label

    def on_add_clicked(self, evt):
        json_path = []
        parent_item = self._fields_tree.currentItem().parent()
        parent_data = parent_item.data(0, Qt.UserRole) if parent_item else None
        if isinstance(parent_data, str):
            json_path.append(parent_data)
        json_path.append(self._field_name)
        json_path = ".".join(json_path)
        operator_obj = self._operators[self._operator.currentIndex()]
        expression = operator_obj.get_comparison_expression(self._field, FieldNamed(json_path), self._value_widget)
        self._search_expression_parts.append(expression)
        self._criteria_list.addItem(f"{underscored_to_words(self._field_name)} {operator_obj.label} {operator_obj.get_value_as_string(self._field, self._value_widget)}")

    @property
    def distance(self):
        return self._distance_field.value()

    def create_conditions(self):
        conditions = []
        if self._search_expression_parts:
            for part in self._search_expression_parts:
                conditions.append(part)
        return conditions
       
    def on_remove_clicked(self, evt):   
        selection = self._criteria_list.currentIndex()
        if selection < 0:
            return
        del self._search_expression_parts[selection]
        self._criteria_list.removeItemWidget(self._criteria_list.currentItem())
