import inspect
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QListWidget, QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QGridLayout, QMenuBar, QApplication, QAction
from osm_db import EntityMetadata
from shapely.geometry.point import Point
from ..humanization_utils import format_field_value, underscored_to_words, describe_entity
from .. import services
from ..geometry_utils import closest_point_to, distance_between, bearing_to, to_shapely_point, to_latlon
from . import object_actions
from .object_actions.action import ObjectAction

def action_execution_handler_factory(action, entity):
    def handler(evt):
        return action.execute(entity)
    return handler

class ObjectsBrowserWindow(QWidget):

    def __init__(self, parent, title, person, unsorted_objects):
        super().__init__(None)
        act = QAction("close", self)
        act.triggered.connect(self.close)
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
        self._objects_list.currentRowChanged.connect(self.on_objects_listbox)
        objects_label.setBuddy(self._objects_list)
        layout.addWidget(self._objects_list, 1, 0)
        props_label = QLabel(_("Object properties"), self)
        layout.addWidget(props_label, 0, 1)
        self._props = QTreeWidget(self)
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
        unsorted_objects = list(unsorted_objects)
        self.setWindowTitle(title + _(" ({num_objects} objects shown)").format(num_objects=len(unsorted_objects)))
        self._person = person
        objects = []
        shapely_point = to_shapely_point(person.position)
        for obj in unsorted_objects:
            closest = closest_point_to(shapely_point, obj.geometry)
            closest_latlon = to_latlon(closest)
            cur_distance = distance_between(closest_latlon, person.position)
            objects.append((cur_distance, obj, closest_latlon))
        objects.sort(key=lambda e: e[0])
        for dist, obj, closest in objects:
            bearing = bearing_to(person.position, closest)
            rel_bearing = (bearing - self._person.direction) % 360
            self._objects_list.addItem(_("{object}: distance {distance:.2f} meters, {rel_bearing:.2f}° relatively").format(object=describe_entity(obj), distance=dist, rel_bearing=rel_bearing))
        self._objects = objects
        self._all_actions = []
        for member in object_actions.__dict__.values():
            if inspect.isclass(member) and issubclass(member, ObjectAction):
                self._all_actions.append(member)
        self._objects_list.setCurrentRow(0)

    def _create_item(self, menu, label, shortcut, callback):
        action = menu.addAction(label)
        action.triggered.connect(callback)
        action.setShortcut(QKeySequence(shortcut))


    def on_goto_clicked(self, evt):
        self._person.move_to(self.selected_object[2])
        self.close()
    
    def on_objects_listbox(self, current_index):
        selected = self._objects[current_index][1]
        self._props.clear()
        common_item = QTreeWidgetItem([_("Common properties")])
        specific_item = QTreeWidgetItem([_("Specific properties")])
        other_item = QTreeWidgetItem([_("Other properties - they can not be searched and are not processed in any way")])
        common_fields = set(EntityMetadata.for_discriminator("OSMEntity").fields.keys())
        selected_metadata = EntityMetadata.for_discriminator(selected.discriminator)
        known_fields = selected_metadata.all_fields
        for field_name in selected.defined_field_names():
            raw_value = selected.value_of_field(field_name)
            if field_name not in known_fields:
                other_item.addChild(QTreeWidgetItem(["%s: %s"%(underscored_to_words(field_name), raw_value)]))
            else:
                value_str = "%s: %s"%(underscored_to_words(field_name), format_field_value(raw_value, known_fields[field_name].type_name))
                if field_name in common_fields:
                    common_item.addChild(QTreeWidgetItem([value_str]))
                else:
                    specific_item.addChild(QTreeWidgetItem([value_str]))
        self._props.addTopLevelItem(common_item)
        if specific_item.childCount() > 0:
            self._props.addTopLevelItem(specific_item)
            self._props.expandItem(specific_item)
            #self._props.setCurrentItem(specific_item) # Breaks focus behavior slightly, but annoingly enough.
        if other_item.childCount() > 0:
            self._props.addTopLevelItem(other_item)
        self._object_actions.clear()
        print("Actions")
        for action in self._all_actions:
            if action.executable(selected):
                mi = self._object_actions.addAction(action.label)
                mi.triggered.connect(action_execution_handler_factory(action, selected))

    @property
    def selected_object(self):
        return self._objects[self._objects_list.currentRow()]

    def on_copypropvalue_selected(self, evt):
        prop = self._props.currentItem().text(0)
        val = prop.split(": ", 1)[1]
        QApplication.clipboard().setText(val)
    
    def on_copypropname_selected(self, evt):
        prop = self._props.currentItem().text(0)
        name = prop.split(": ", 1)[0]
        QApplication.clipboard().setText(name)
    
    def on_copypropline_selected(self, evt):
        prop = self._props.currentItem().text(0)
        QApplication.clipboard().setText(prop)