from enum import Enum
from datetime import datetime

def extended_types_encoder(value):
    if isinstance(value, Enum):
        return value.value
    elif isinstance(value, datetime):
        return value.isoformat()
    else:
        raise TypeError("Unknown type %s."%type(value))