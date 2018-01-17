import inflection
import redbaron
from pathlib import Path
from .utils import is_valid_identifier, red_baron_from_file, is_nonascii
from .model import Model


class EnumInfo:
    def __init__(self, path, enum_class):
        self.path = path
        self.members = set()
        for assignment in enum_class.find_all("assign"):
            self.members.add(assignment.target.value)

class Enum:
    known = {}
    shared_enums_path = Path("shared")/"models"/"enums.py"

    @classmethod
    def with_member_names(cls, names):
        choices = []
        if not cls.known:
            cls._build_info_map()
        for name, enum in cls.known.items():
            if names.issubset(enum.members):
                choices.append(name)
        return choices
    @classmethod
    def _build_info_map(cls):
        print("Building enum info map...")
        for fname in (Path("shared")/"models").glob("*.py"):
            m = red_baron_from_file(fname)
            for item in m.find_all("class"):
                base = item.inherit_from[0]
                if isinstance(base, redbaron.NameNode):
                    base_name = base.value
                else: # It is a dotted identifier
                    base_name = base[-1].value
                if base_name == "Enum":
                    if item.name in cls.known:
                        raise RuntimeError("Duplicate enum %s."%item.name)
                    cls.known[item.name] = EnumInfo(fname, item)

    @staticmethod
    def create_in(destination, name, member_names):
        if name in Enum.known:
            raise ValueError("Refusing to create a duplicate of %s."%name)
        if not is_valid_identifier(name):
            raise ValueError("Invalid enum name %s."%name)
        code = "class %s(enum.Enum):\n"%name
        member_value = 0
        for member in member_names:
            if not is_valid_identifier(member):
                raise ValueError("The member %s is not a valid python identifier."%member)
            code += "    %s = %s\n"%(member, member_value)
            member_value += 1
        code += "\n"
        if isinstance(destination, Enum):
            module = destination._module
            path = destination._file
            insertion_idx = len(module)
        elif isinstance(destination, Model):
            module = destination._model_module
            path = destination._model_file
            insertion_idx = module.index(destination._model_class)
        module.insert(insertion_idx, code)
        destination.save()
        Enum.known[name] = EnumInfo(path, module[insertion_idx])
            
    def __init__(self, name):
        if not Enum.known:
            Enum._build_info_map()
        if name not in Enum.known:
            raise ValueError("Non existent enum %s."%name)
        self._info = Enum.known[name]
        self._file = self._info.path
        self._enum_module = red_baron_from_file(self._file)
        self._enum_class = self._enum_module.find("class", name=name)
        last_assignment = self._enum_class.find_all("assign")[-1]
        self._insertion_idx = self._enum_class.index(last_assignment) + 1
        self._last_value = int(last_assignment.value.value)

    def add_member(self, name):
        if not is_valid_identifier(name):
            raise ValueError("%s is not a valid python identifier."%name)
        if is_nonascii(name):
            raise ValueError("%s is not an ascii only identifier, unicode support is missing in baron."%name)
        if name in self._info.members:
            return
        next_free = self._last_value + 1
        self._enum_class.insert(self._insertion_idx, "%s = %s"%(name, next_free))
        self._insertion_idx += 1
        self._last_value = next_free
        self._info.members.add(name)
    
    def save(self):
        self._file.write_text(self._enum_module.dumps(), encoding="utf-8")

    @property
    def shared(self):
        return self._file.name == "enums.py"

    def make_shared(self):
        if self.shared:
            return
        # First, move the enum to the enums.py file.
        self._enum_module.remove(self._enum_class)
        self.save()
        shared_enums = red_baron_from_file(Enum.shared_enums_path)
        shared_enums.append(self._enum_class)
        # Add the import to the original module
        model = Model(inflection.camelize(self._info.path.name.replace(".py", "")))
        model.add_shared_enum_import(self._enum_class.name)
        model.save()
        # Update the metadata so future operations are valid
        self._enum_module = shared_enums
        self._info.path = Enum.shared_enums_path
        self._file = self._info.path
        Enum.known[self._enum_class.name] = self._info
        self.save()