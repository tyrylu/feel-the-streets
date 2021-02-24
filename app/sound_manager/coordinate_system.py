from enum import Enum, auto

class CoordinateSystem(Enum):
    openal = auto()
    cartesian_right_handed = auto()
    
    def translate_coordinates(self, x, y, z):
        if self is CoordinateSystem.openal:
            return x, y, z
        elif self is CoordinateSystem.cartesian_right_handed:
            return x, z, -y