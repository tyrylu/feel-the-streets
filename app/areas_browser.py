from PySide6.QtWidgets import QLabel, QListWidget
from .base_dialog import BaseDialog
from .humanization_utils import underscored_to_words

class AreasBrowserDialog(BaseDialog):

    def __init__(self, parent, area_name, areas):
        super().__init__(parent, _("Select the area you mean"), _("&Select"), _("&Close"))
        self._areas = list(areas.items())
        for _id, (parent_name, _data) in self._areas:
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
        for key, value in self._areas[index][1][1].items():
            self._area_props.addItem(f"{underscored_to_words(key)}: {value}")
        self._area_props.addItem(_("Area id: {}").format(self._areas[index][0]))

    @property
    def selected_area_id(self):
        return self._areas[self._areas_list.currentRow()][0]