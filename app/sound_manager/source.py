import openal

class Source(openal.Source):
    def __init__(self, buffer, destroy_buffer, coordinates_divider, coordinate_decimal_places):
        super().__init__(buffer, destroy_buffer)
        self._coordinate_decimal_places = coordinate_decimal_places
        self._coordinates_divider = coordinates_divider

    def _transform_coordinate(self, coordinate):
        if self._coordinate_decimal_places:
            coordinate = round(coordinate, self._coordinate_decimal_places)
        return coordinate/self._coordinates_divider

    def _transform_coords(self, coords):
        return [self._transform_coordinate(coord) for coord in coords]

    def set_position(self, pos):
        super().set_position(self._transform_coords(pos))
