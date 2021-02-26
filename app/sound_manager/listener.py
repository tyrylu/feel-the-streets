import openal
from .coordinates_transformer import CoordinatesTransformer

class Listener(openal.Listener):
    def __init__(self, coordinates_divider, coordinate_decimal_places, coordinate_system, origin):
        super().__init__()
        self._transformer = CoordinatesTransformer(coordinates_divider, coordinate_decimal_places, coordinate_system, origin)
        
    def set_position(self, pos):
        transformed_coords = self._transformer.transform_coordinates(pos)
        super().set_position(transformed_coords)