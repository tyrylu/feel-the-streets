import inspect
from PySide6.QtGui import QKeySequence, QAction, Qt
from PySide6.QtWidgets import QWidget, QListWidget, QTreeWidgetItem, QPushButton, QLabel, QGridLayout, QMenuBar, QApplication
from osm_db import EntityMetadata
from ..humanization_utils import format_field_value, underscored_to_words, format_relationship
from ..services import menu_service
from ..more_accessible_tree_widget import MoreAccessibleTreeWidget
from . import object_actions
from .object_actions.action import ObjectAction
from .objects_sorter import ObjectsSorter

def action_execution_handler_factory(action, entity, window):
    def handler():
        return action.execute(entity, window)
    return handler

class ObjectsBrowserWindow(QWidget):

    def __init__(self, title, person, unsorted_objects, autoshow=True, progress_indicator=None):
        super().__init__(None)
        act = QAction("close", self)
        act.triggered.connect(self._do_close)
        act.setShortcut(QKeySequence("escape"))
        self.addAction(act)
        layout = QGridLayout()
        bar = QMenuBar(self)
        self._object_actions = bar.addMenu(_("Object actions"))
        property_actions = bar.addMenu(_("Property actions"))
        self._create_item(property_actions, _("Copy property value"), "ctrl+c", self.on_copypropvalue_selected)
        self._create_item(property_actions, _("Copy property name"), "alt+c", self.on_copypropname_selected)
        self._create_item(property_actions, _("Copy property name and value"), "ctrl+alt+c", self.on_copypropline_selected)
        objects_label = QLabel(_("Objects"), self)
        layout.addWidget(objects_label, 0, 0)
        self._objects_list = QListWidget(self)
        self._objects_list.setAccessibleName(objects_label.text())
        self._objects_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._objects_list.currentRowChanged.connect(self.on_objects_listbox)
        self._objects_list.customContextMenuRequested.connect(self._on_objects_list_menu)
        objects_label.setBuddy(self._objects_list)
        layout.addWidget(self._objects_list, 1, 0)
        props_label = QLabel(_("Object properties"), self)
        layout.addWidget(props_label, 0, 1)
        self._props = MoreAccessibleTreeWidget(self)
        self._props.setAccessibleName(props_label.text())
        props_label.setBuddy(self._props)
        layout.addWidget(self._props, 1, 1)
        goto_button = QPushButton(_("Go to"), self)
        goto_button.setDefault(True)
        goto_button.clicked.connect(self.on_goto_clicked)
        self._objects_list.itemActivated.connect(goto_button.click)
        layout.addWidget(goto_button, 2, 0)
        close_button = QPushButton(_("Close"), self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, 2, 1)
        self.setLayout(layout)
        self.setWindowTitle(title + _(" ({num_objects} objects shown)").format(num_objects=len(unsorted_objects)))
        self._person = person
        self._autoshow = autoshow
        self._progress_indicator = progress_indicator
        self._all_actions = []
        for member in object_actions.__dict__.values():
            if inspect.isclass(member) and issubclass(member, ObjectAction):
                self._all_actions.append(member)
        self._objects_list.setCurrentRow(0)
        self._sorter = ObjectsSorter(unsorted_objects, person)
        self._sorter.objects_sorted.connect(self._objects_sorted)
        self._sorter.start()
    
    def _objects_sorted(self, rels):
        self._rels = rels
        for rel in rels:
            self._objects_list.addItem(format_relationship(rel))
        if self._progress_indicator:
            self._progress_indicator.hide()
            self._progress_indicator.deleteLater()
        if self._autoshow:
            self._objects_list.setCurrentRow(0)
            self.show()

    def _create_item(self, menu, label, shortcut, callback):
        action = menu.addAction(label)
        action.triggered.connect(callback)
        action.setShortcut(QKeySequence(shortcut))

    def on_goto_clicked(self):
        self._person.move_to(self.selected_object.closest_point, force=True)
        self.close()
        
    def _do_close(self):
        self.close()
        self.destroy()
        windows = QApplication.topLevelWidgets()
        other_browsers = [w for w in windows if w is not self and isinstance(w, self.__class__) and w.isVisible()]
        if other_browsers:
            other_browsers[-1].activateWindow()
        else:
            menu_service().ensure_key_capturer_focus()
    
    def on_objects_listbox(self, current_index):
        selected = self._rels[current_index].entity
        self._props.clear()
        common_item = QTreeWidgetItem([_("Common properties")])
        specific_item = QTreeWidgetItem([_("Specific properties")])
        other_item = QTreeWidgetItem([_("Other properties - they can not be searched and are not processed in any way")])
        other_item.setData(0, Qt.AccessibleTextRole, "Override")
        common_fields = list(EntityMetadata.for_discriminator("OSMEntity").fields.keys())
        selected_metadata = EntityMetadata.for_discriminator(selected.discriminator)
        known_fields = selected_metadata.all_fields
        formatted_values = {}
        for field_name in selected.defined_field_names():
            raw_value = selected.value_of_field(field_name)
            if field_name not in known_fields:
                # By the mere fact that the other fields have no defined order, we can add them there without losing anything.
                other_item.addChild(QTreeWidgetItem(["%s: %s"%(underscored_to_words(field_name), raw_value)]))
            else:
                value_str = "%s: %s"%(underscored_to_words(field_name), format_field_value(raw_value, known_fields[field_name].type_name))
                formatted_values[field_name] = value_str
        for common in common_fields:
            del known_fields[common]
            common_item.addChild(QTreeWidgetItem([formatted_values[common]]))
        for specific in known_fields.keys(): # Because we deleted the common ones in the loop before this, only the specific remain.
            if specific in formatted_values:
                specific_item.addChild(QTreeWidgetItem([formatted_values[specific]]))
        # We add the entity ID mainly for debugging purposes, and that's the reason why it is added the last and so special in the first place.
        common_item.addChild(QTreeWidgetItem([_("Object id: {}").format(selected.id)]))
        self._props.addTopLevelItem(common_item)
        if specific_item.childCount() > 0:
            self._props.addTopLevelItem(specific_item)
            self._props.expandItem(specific_item)
            #self._props.setCurrentItem(specific_item) # Breaks focus behavior slightly, but annoingly enough.
        if other_item.childCount() > 0:
            self._props.addTopLevelItem(other_item)
        self._object_actions.clear()
        for action in self._all_actions:
            if action.executable(selected):
                mi = self._object_actions.addAction(action.label)
                mi.triggered.connect(action_execution_handler_factory(action, selected, self))

    @property
    def selected_object(self):
        return self._rels[self._objects_list.currentRow()]

    def on_copypropvalue_selected(self):
        prop = self._props.currentItem().text(0)
        val = prop.split(": ", 1)[1]
        QApplication.clipboard().setText(val)
    
    def on_copypropname_selected(self):
        prop = self._props.currentItem().text(0)
        name = prop.split(": ", 1)[0]
        QApplication.clipboard().setText(name)
    
    def on_copypropline_selected(self):
        prop = self._props.currentItem().text(0)
        QApplication.clipboard().setText(prop)

    def _on_objects_list_menu(self, point):
        self._object_actions.exec_(point)