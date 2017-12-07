import redbaron
from pathlib import Path
from .utils import is_valid_identifier, red_baron_from_file


class EnumInfo:
    def __init__(self, path, enum_class):
        self.path = path
        self.members = set()
        for assignment in enum_class.find_all("assign"):
            self.members.add(assign.target.value)

class Enum:
    known = {}

    @classmethod
    def with_member_names(cls, names):
        choices = []
        if not cls.known:
            cls._build_info_map()
        for name, enum in cls.known.values():
            if names.issubset(enum.members):
                choices.append(name)
        return choices
    @classmethod
    def _build_info_map(cls):
        for fname in (Path("shared")/"models").glob("*.py"):
            m = red_baron_from_file(fname)
            for item in m.find_all("class"):
                base = item.inherit_from[0]
                if isinstance(base, redbaron.NameNode):
                    base_name = base.value
                else: # It is a dotted identifier
                    base_name = base[-1].value
                if base_name == "Enum":
                    cls.known[item.name] = EnumInfo(fname, item)

    def __init__(self, name):
        if not Enum.known:
            Enum._build_info_map()
        if name not in Enum.known:
            raise ValueError("Non existent enum %s."%name)
        self._file = Enum.known[name]
        self._enum_module = red_baron_from_file(self._file)
        self._enum_class = self._enum_module.find("class", name=name)
        self._last_value = int(self._enum_class[-1].value.value)

    def add_member(self, name):
        if not is_valid_identifier(name):
            raise ValueError("%s is not a valid python identifier."%name)
        next_free = self._last_value + 1
        self._enum_class.append("%s = %s"%(name, next_free))
        self._last_value = next_free
    
    def save(self):
        self._file.write_text(self._enum_module.dumps())