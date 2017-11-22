import pint
from pint import _APP_REGISTRY as registry
import sqlalchemy.types as types

class DimensionalFloat(types.TypeDecorator):
    """A type storing a float with its unit. On the database side only the converted float is stored, on the python side a pint.Quantity is returned and expected."""
    
    impl = types.Float

    def __init__(self, canonical_unit, *args, **kwargs):
        if not isinstance(canonical_unit, str):
            raise ValueError("A string unit specification is required.")
        self._canonical_unit = canonical_unit
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None and isinstance(value, pint.Quantity):
            return value.to(self._canonical_unit).magnitude
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return registry("%s %s"%(value, self._canonical_unit))

