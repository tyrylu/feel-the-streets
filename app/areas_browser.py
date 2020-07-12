from PySide2.QtWidgets import QDialog, QGridLayout, QLabel, QListWidget, QPushButton
from .humanization_utils import underscored_to_words

class AreasBrowserDialog(QDialog):

    def __init__(self, parent, areas):
        super().__init__(parent)
        self.setWindowTitle(_("Select the area you mean"))
        layout = QGridLayout()
        areas_label = QLabel(_("Areas"))
        layout.addWidget(areas_label, 0, 0)
        self._areas_list = QListWidget(self)
        areas_label.setBuddy(self._areas_list)
        self._areas_list.currentRowChanged.connect(self.on_areas_list_listbox)
        layout.addWidget(self._areas_list, 1, 0)
        props_label = QLabel(_("Area properties"))
        layout.addWidget(props_label, 0, 1)
        self._area_props = QListWidget()
        props_label.setBuddy(self._area_props)
        layout.addWidget(self._area_props, 1, 1)
        select_button = QPushButton("Select")
        select_button.setDefault(True)
        select_button.clicked.connect(self.accept)
        layout.addWidget(select_button, 2, 0)
        close_button = QPushButton(_("&Close"))
        close_button.clicked.connect(self.reject)
        layout.addWidget(close_button, 2, 1)
        self.setLayout(layout)
        self._areas = list(areas.items())
        for id, data in self._areas:
            self._areas_list.addItem(_("Area {id}").format(id=id))
        self._areas_list.setCurrentRow(0)

    def on_areas_list_listbox(self, index):
        self._area_props.clear()
        for key, value in self._areas[index][1].items():
            self._area_props.addItem(f"{underscored_to_words(key)}: {value}")

    @property
    def selected_area_id(self):
        return self._areas[self._areas_list.currentRow()][0]