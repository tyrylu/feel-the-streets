import logging
from PySide2.QtWidgets import QLabel, QListWidget
from .base_dialog import BaseDialog
from .humanization_utils import underscored_to_words
from .server_interaction.http import get_area_parents

log = logging.getLogger(__name__)

class AreasBrowserDialog(BaseDialog):

    def __init__(self, parent, area_name, areas):
        super().__init__(parent, _("Select the area you mean"), _("&Select"), _("&Close"))
        self._areas = list(areas.items())
        for id, data in self._areas:
            parents = get_area_parents(id)
            if len(parents) > 1:
                log.warning("Area with id %s has multiple parents, falling back on the first.", id)
            if parents:
                parent_name = next(iter(parents.values()))["name"]
            else:
                parent_name = _("not known")
            self._areas_list.addItem(_("{area_name}, {parent_name}").format(area_name=area_name, parent_name=parent_name))
        self._areas_list.setCurrentRow(0)

    def create_ui(self):
        areas_label = QLabel(_("Areas"))
        self.layout.addWidget(areas_label, 0, 0)
        self._areas_list = QListWidget(self)
        areas_label.setBuddy(self._areas_list)
        self._areas_list.currentRowChanged.connect(self.on_areas_list_listbox)
        self.layout.addWidget(self._areas_list, 1, 0)
        props_label = QLabel(_("Area properties"))
        self.layout.addWidget(props_label, 0, 1)
        self._area_props = QListWidget()
        props_label.setBuddy(self._area_props)
        self.layout.addWidget(self._area_props, 1, 1)

    def on_areas_list_listbox(self, index):
        self._area_props.clear()
        for key, value in self._areas[index][1].items():
            self._area_props.addItem(f"{underscored_to_words(key)}: {value}")

    @property
    def selected_area_id(self):
        return self._areas[self._areas_list.currentRow()][0]