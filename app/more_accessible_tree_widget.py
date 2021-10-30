from PySide6.QtWidgets import QTreeWidget
from PySide6.QtGui import Qt, QAccessible, QAccessibleStateChangeEvent

def get_expansion_state_string(is_expanded):
    if is_expanded:
        return _("expanded")
    else:
        return _("collapsed")

def set_accessible_text(item):
    acc_text = f"{item.text(0)} {get_expansion_state_string(item.isExpanded())}"
    item.setData(0, Qt.AccessibleTextRole, acc_text)

class MoreAccessibleTreeWidget(QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._seen_items = set()
        self.model().rowsInserted.connect(self._on_rows_inserted)
        self.itemCollapsed.connect(self._on_item_collapsed)
        self.itemExpanded.connect(self._on_item_expanded)

    def _on_rows_inserted(self, parent, start, end):
        item = self.itemFromIndex(parent)
        if not item: # We inserted a top level item
            get_child = self.topLevelItem
        else:
            get_child = item.child
        for idx in range(start, end + 1):
            self._set_initial_status(get_child(idx))
        
    def _set_initial_status(self, item):
        parent = item.parent()
        if parent and parent not in self._seen_items:
            self._seen_items.add(parent)
            self._set_initial_status(parent)
        if item.childCount():
            set_accessible_text(item)

    def _on_item_collapsed(self, item):
        set_accessible_text(item)

    def _on_item_expanded(self, item):
        set_accessible_text(item)
        