from enum import Enum

def extended_types_encoder(value):
    if isinstance(value, Enum):
        return value.value
    else:
        raise TypeError("Unknown type %s."%value)