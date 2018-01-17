from pathlib import Path
import inflection
import redbaron
from .utils import red_baron_from_file

class Model:
    def __init__(self, class_name):
        file_name = "%s.py"%inflection.underscore(class_name)
        self._model_file = Path("shared")/"models"/file_name
        self._generator_file = Path("fts_tool")/"database_updater"/"generators"/file_name
        self._model_module = red_baron_from_file(self._model_file)
        self._generator_module = red_baron_from_file(self._generator_file)
        self._model_class = self._model_module.find("class", class_name)
        self._generator_class = self._generator_module.find("class", class_name + "Generator")
        assignments = self._model_class.find_all("assign")
        assignments = [a for a in assignments if isinstance(a.parent, redbaron.ClassNode)]
        self._column_names = [ass.target.value for ass in assignments]
        self._last_assignment_idx = self._model_class.index(assignments[-1]) + 1
        self._generator_init = self._generator_class.find("def", name="__init__")
        self._shared_enums_import = [imp for imp in self._model_module.find_all("from_import") if imp.name and imp.name.value == "enums"]
        if not self._shared_enums_import:
            self._shared_enums_import = None
        else:
            self._shared_enums_import = self._shared_enums_import[0]

    def add_property(self, property_name, column_name, column_type):
        if column_name in self._column_names:
            return
        self._model_class.insert(self._last_assignment_idx, "%s = Column(%s)"%(column_name, column_type))
        self._last_assignment_idx += 1
        if column_name != property_name:
            self._generator_init.append("self.renames(\"%s\", \"%s\")"%(property_name, column_name))
    
    def save(self):
        self._model_file.write_text(self._model_module.dumps(), encoding="utf-8")
        self._generator_file.write_text(self._generator_module.dumps(), encoding="utf-8")

    def add_shared_enum_import(self, name):
        if name not in self.imported_shared_enums:
            if not self._shared_enums_import:
                self._create_shared_enums_import(name)
            else:
                self._shared_enums_import.targets.append(name)
            return True
        return False

    @property
    def imported_shared_enums(self):
        if self._shared_enums_import:
            return [t.value for t in self._shared_enums_import.targets]
        else:
            return []

    def _create_shared_enums_import(self, first_name):
        import_expr = redbaron.RedBaron("from .enums import %s"%first_name)[0]
        last_from_import = self._model_module.find_all("from_import")
        idx = self._model_module.index(last_from_import)
        self._model_module.insert(idx, import_expr)