from pathlib import Path
from .utils import red_baron_from_file

class Model:
    def __init__(self, class_name):
        file_name = "%s.py"%class_name.lower()
        self._model_file = Path("shared")/"models"/file_name
        self._generator_file = Path("fts_tool"/"db_updater"/"generators"/file_name
        self._model_module = red_baron_from_file(self._model_file)
        self._generator_module = red_baron_from_file(self._generator_file)
        self._model_class = self._model_module.find("class", class_name)
        self._generator_class = self._generator_module.find("class", class_name + "Generator")
        self._last_assignment_idx = self._model_class.index(self._model_class.find_all("assign")[-1])
        self._generator_init = self._generator_class.find("def", name="__init__")

    def add_property(self, property_name, column_name, column_type):
        self._model_class.insert(self._last_assignment_idx, "%s = Column(%s"%(column_name, column_type))
        self._last_assignment_idx += 1
        if column_name != property_name:
            self._generator_init.append("self.renames(\"%s\", \"%s\")"%(property_name, column_name))
    def save(self):
        self._model_file.write_text(self._model_module.dumps())
        self._generator_file.write_text(self._generator_module.dumps())

