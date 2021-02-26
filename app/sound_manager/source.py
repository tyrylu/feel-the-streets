import openal
from .coordinates_transformer import CoordinatesTransformer

class Source(openal.Source):
    def __init__(self, buffer, destroy_buffer, coordinates_divider, coordinate_decimal_places, coordinate_system, origin):
        super().__init__(buffer, destroy_buffer)
        self._transformer = CoordinatesTransformer(coordinates_divider, coordinate_decimal_places, coordinate_system, origin)
        
    def set_position(self, pos):
        transformed_pos = self._transformer.transform_coordinates(pos)
        super().set_position(transformed_pos)
