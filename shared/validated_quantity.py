import pint
from .services import unit_registry

ureg = unit_registry()
OriginalQuantity = ureg.Quantity
class Quantity(OriginalQuantity):
    @classmethod
    def get_validators(cls):
        yield cls.validate_quantity

    @classmethod
    def validate_quantity(cls, value):
        if isinstance(value, ureg.Quantity):
            return value
        try:
            ureg.Quantity = cls
            return ureg("%s %s"%(cls.canonical_unit, value))
        except pint.UndefinedUnitError:
            raise TypeError(f"{value} could not be converted to a quantity.")


def quantity(canonical_unit):
    return type("CanonicalQuantity", (Quantity,), dict(canonical_unit=canonical_unit))

