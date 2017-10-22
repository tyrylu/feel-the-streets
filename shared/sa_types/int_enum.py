import enum
from sqlalchemy import util
import sqlalchemy.types as types
from sqlalchemy.sql.elements import TypeCoerce as type_coerce, _defer_name
import sqlalchemy.sql.schema as schema

class IntEnum(types.TypeDecorator, types.SchemaType):
    """A type storing the members of an enum as ints in the database."""
    
    impl = types.Integer

    def __init__(self, enum_class, *args, **kwargs):
        if not issubclass(enum_class, enum.Enum):
            raise ValueError("Only enums are allowed.")
        self._enum_class = enum_class
        self.name = self._enum_class.__name__.lower()
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None and isinstance(value, self._enum_class):
            return self._enum_class(value).value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return self._enum_class(value)

    def _should_create_constraint(self, compiler, **kw):
        return True
    
    def _set_table(self, column, table):
        enum_vals = ", ".join(str(m.value) for m in self._enum_class.__members__.values())
        variant_mapping = self._variant_mapping_for_set_table(column)
        e = schema.CheckConstraint(
            "%s IN (%s)"%(column.name, enum_vals),
            name=_defer_name(self.name),
            _create_rule=util.portable_instancemethod(
                self._should_create_constraint,
                {"variant_mapping": variant_mapping}),
            _type_bound=True
        )
        table.append_constraint(e)
        
