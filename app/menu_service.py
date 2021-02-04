from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction, QWidget

def safe_set_checked(target, new_state):
    target.blockSignals(True)
    target.setChecked(new_state)
    target.blockSignals(False)

class MenuService:
    def __init__(self, app_window):
        self._window = app_window
        # No idea why, but if we add the child widget when the window is shown, it either doesn't get added or it doesn't get keyboard focus, no idea which of these two actually happens.
        app_window.hide()
        self._key_capturer = QWidget(self._window)
        self._key_capturer.setFocus()
        app_window.show()
        self._menubar = app_window.menuBar()
        self._menu_items_by_name = {}
        self._menus = {}
    
    def _menu_item_callables(self, source):
        for member_name in source.__class__.__dict__.keys():
            member_obj = getattr(source, member_name)
            if hasattr(member_obj, "item_label"):
                yield member_obj

    def register_menu_commands(self, source):
        for cmd in self._menu_item_callables(source):
            self.register_menu_command(cmd)

    def register_menu_command(self, cmd):
        menu_path = cmd.menu.split("/")
        menu = self._ensure_menu(menu_path)
        label = cmd.item_label
        if cmd.item_shortcut:
            label += "\t%s"%cmd.item_shortcut
        item = QAction(label, self._key_capturer)
        item.setShortcutContext(Qt.WidgetShortcut)
        # We must add a separate action to the menu, otherwise the shortcut is being triggered even when the menubar is focused.
        menu_action = menu.addAction(label)
        self._key_capturer.addAction(item)
        item.triggered.connect(cmd)
        menu_action.triggered.connect(cmd)
        item.setCheckable(cmd.checkable)
        menu_action.setCheckable(cmd.checkable)
        if cmd.item_shortcut:
            seq = QKeySequence(cmd.item_shortcut)
            item.setShortcut(seq)
        if cmd.item_name:
            self._menu_items_by_name[cmd.item_name] = menu_action
        if cmd.checkable:
            item.toggled.connect(lambda checked, mi=menu_action: safe_set_checked(mi, checked))
            menu_action.toggled.connect(lambda checked, si=item: safe_set_checked(si, checked))
    
    def _ensure_menu(self, path, parent=None):
        if tuple(path) in self._menus:
            return self._menus[tuple(path)]
        # Find the highest level which still exists.
        parent = None
        must_create = []
        while True:
            try:
                component = path.pop()
                must_create.append(component)
                if tuple(path) in self._menus:
                    parent = self._menus[tuple(path)]
                    break # Found our child.
            except IndexError:
                break
        if not parent:
            parent = self._menubar
        while True:
            try:
                menu_name = must_create.pop()
                parent = parent.addMenu(menu_name)
                path.append(menu_name)
                self._menus[tuple(path)] = parent
            except IndexError:
                return parent

    def menu_item_with_name(self, name):
        return self._menu_items_by_name[name]

    def ensure_key_capturer_focus(self):
        self._window.activateWindow()
        self._key_capturer.setFocus()

def menu_command(menu, label, shortcut=None, name=None, checkable=False):
    def wrap(func):
        func.menu = menu
        func.item_label = label
        func.item_shortcut = shortcut
        func.item_name = name
        func.checkable = checkable
        return func
    return wrap

