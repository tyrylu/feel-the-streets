import openal
from .coordinates_transformer import CoordinatesTransformer

class Listener(openal.Listener):
    def __init__(self, coordinates_divider, coordinate_decimal_places, coordinate_system, origin):
        super().__init__()
        self._transformer = CoordinatesTransformer(coordinates_divider, coordinate_decimal_places, coordinate_system, origin)
        
    def set_position(self, pos):
        transformed_coords = self._transformer.transform_coordinates(pos)
        print(f"Set listener pos to {transformed_coords}")
        super().set_position(transformed_coords)