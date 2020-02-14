from PySide2.QtGui import QKeySequence

class MenuService:
    def __init__(self, menubar):
        self._menubar = menubar
        self._menu_items_by_name = {}
        self._menus = {}
    
    def _menu_item_callables(self, source):
        for member_name in source.__class__.__dict__.keys():
            member_obj = getattr(source, member_name)
            if hasattr(member_obj, "item_label"):
                yield member_obj

    def register_menu_commands(self, source):
        for cmd in self._menu_item_callables(source):
            menu_path = cmd.menu.split("/")
            menu = self._ensure_menu(menu_path)
            label = cmd.item_label
            if cmd.item_shortcut:
                label += "\t%s"%cmd.item_shortcut
            item = menu.addAction(label)
            item.triggered.connect(cmd)
            if cmd.item_shortcut:
                item.setShortcut(QKeySequence(cmd.item_shortcut))
            if cmd.item_name:
                self._menu_items_by_name[cmd.item_name] = item
    
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


def menu_command(menu, label, shortcut, name=None):
    def wrap(func):
        func.menu = menu
        func.item_label = label
        func.item_shortcut = shortcut
        func.item_name = name
        return func
    return wrap

