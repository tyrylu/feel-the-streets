import openal

class Source(openal.Source):
    def __init__(self, buffer, destroy_buffer, coordinates_divider, coordinate_decimal_places, coordinate_system):
        super().__init__(buffer, destroy_buffer)
        self._coordinate_decimal_places = coordinate_decimal_places
        self._coordinates_divider = coordinates_divider
        self._coordinate_system = coordinate_system

    def _transform_coordinate(self, coordinate):
        if self._coordinate_decimal_places:
            coordinate = round(coordinate, self._coordinate_decimal_places)
        return coordinate/self._coordinates_divider

    def _transform_coords(self, coords):
        return [self._transform_coordinate(coord) for coord in coords]

    def set_position(self, pos):
        x, y, z = self._transform_coords(pos)
        x, y, z = self._coordinate_system.translate_coordinates(x, y, z)
        z += 550000
        print(f"Set source pos to {(x, y, z)}")
        super().set_position([x, y, z])
