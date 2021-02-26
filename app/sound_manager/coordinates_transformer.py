class CoordinatesTransformer:
    def __init__(self, coordinates_divider, coordinate_decimal_places, coordinate_system, origin):
        self._divider = coordinates_divider
        self._decimal_places = coordinate_decimal_places
        self._system = coordinate_system
        self._origin = origin

    def _transform_coordinate(self, coordinate):
        if self._decimal_places:
            coordinate = round(coordinate, self._decimal_places)
        return coordinate/self._divider

    def transform_coordinates(self, coords):
        # First, adjust the coordinates to be closer to the sound stage origin
        x, y, z = coords
        if self._origin:
            origin_x, origin_y, origin_z = self._origin
            x -= origin_x
            y -= origin_y
            z -= origin_z
        # Now, apply rounding and scaling
        x, y, z = (self._transform_coordinate(x), self._transform_coordinate(y), self._transform_coordinate(z))
        # And finally map the user's coordinate system to the Openal's one
        return self._system.translate_coordinates(x, y, z)
