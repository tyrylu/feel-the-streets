import logging
import shapely.wkb as wkb
import shapely.geometry as geometry
from shapely.geometry.linestring import LineString
import pydantic
from pygeodesy.ellipsoidalVincenty import LatLon, VincentyError
from .measuring import measure

log = logging.getLogger(__name__)

def to_shapely_point(latlon):
    return geometry.point.Point(latlon.lon, latlon.lat)

def to_latlon(shapely_point):
    return LatLon(shapely_point.y, shapely_point.x)

def distance_between(point1, point2):
    try:
        return point1.distanceTo(point2)
    except VincentyError:
        return 0

def bearing_to(initial, target):
    try:
        return initial.initialBearingTo(target)
    except:
        return 0

def bearings_to(initial, target):
    try:
        dist, initial, final = initial.distanceTo3(target)
        return initial, final
    except:
        return 0, 0

class LineSegment(pydantic.BaseModel):
    line: LineString
    start: geometry.point.Point
    end: geometry.point.Point
    length: float = None
    angle: float = None
    end_angle: float = None
    current: bool = False

    class Config:
        arbitrary_types_allowed = True

    def calculate_length(self):
        self.length = distance_between(to_latlon(self.start), to_latlon(self.end))

    def calculate_angle(self):
        self.angle, self.end_angle = bearings_to(to_latlon(self.start), to_latlon(self.end))

def merge_similar_line_segments(line_segments, precision):
    """Merges adjacent line segments whose angle is same after rounding to a particular precision."""
    merged = []
    first_segment = line_segments[0]
    first_segment.calculate_angle()
    current_segment = first_segment
    current_angle = round(first_segment.angle, precision)
    for segment in line_segments:
        segment.calculate_angle()
        if round(segment.angle, precision) == current_angle:
            current_segment = LineSegment(start=current_segment.start, end=segment.end, line=LineString([current_segment.line.coords[0], segment.line.coords[1]]))
        else:
            merged.append(current_segment)
            current_segment = segment
            current_angle = round(current_segment.angle, precision)
    merged.append(current_segment) # We must add this one manually because it did not have time to be replaced by another one
    return merged

def get_line_segments(line):
    x_coords, y_coords = line.coords.xy
    num_coords = len(x_coords) - 1 # Every segment must have two points, so for example, for two points we get one segment, for three segments we get two, etc.
    segments = []
    for segment in range(num_coords):
        x1, y1 = x_coords[segment], y_coords[segment]
        x2, y2 = x_coords[segment + 1], y_coords[segment + 1]
        line_segment = LineString([(x1, y1),(x2, y2)])
        segments.append(LineSegment(line=line_segment, start=geometry.point.Point(x1, y1), end=geometry.point.Point(x2, y2)))
    return segments

def find_closest_line_segment_of(segments, point):
    min_dist = 10**20
    best_segment = None
    for line_segment in segments:
        dist = line_segment.line.distance(point)
        if dist < min_dist:
            min_dist = dist
            best_segment = line_segment
    best_segment.current = True
    return best_segment

def get_closest_line_segment(point, line):
    return find_closest_line_segment_of(get_line_segments(line), point)

def xy_ranges_bounding_square(center_latlon, side):
    # First, get the x bounds
    side1 = center_latlon.destination(side/2, 0)
    edge1 = side1.destination(side/2, 270)
    min_x = edge1.lon
    max_y = edge1.lat
    edge2 = side1.destination(side/2, 90)
    max_x = edge2.lon
    edge3 = edge2.destination(side, 180)
    min_y = edge3.lat
    # Note that if the square would be positioned just right, the max/min invariants would not hold, but for the foreseeable future usages it should be okay.
    return min_x, min_y, max_x, max_y

def closest_point_from_geoms(geoms, point):
    min = float("inf")
    min_point = None
    for geom in geoms:
        geom_point = closest_point_to(point, geom, convert=False)
        dist = point.distance(geom_point)
        if dist < min:
            min = dist
            min_point = geom_point
    return min_point

def closest_point_to(point, geom, convert=True):
    if convert:
        geom = wkb.loads(geom)
    if geom.geom_type == "Point":
        return geom
    elif geom.geom_type == "LineString":
        return geom.interpolate(geom.project(point))
    elif geom.geom_type == "Polygon":
        return geom.exterior.interpolate(geom.exterior.project(point))
    elif geom.geom_type in {"GeometryCollection", "MultiPolygon"}:
        return closest_point_from_geoms(geom.geoms, point)
    else:
        raise RuntimeError("Can not process geometry of type %s."%geom.geom_type)

def get_road_section_angle(pov, road):
    pov_point = to_shapely_point(pov.position)
    road_line = wkb.loads(road.geometry)
    closest_segment = get_closest_line_segment(pov_point, road_line)
    closest_segment.calculate_angle()
    return closest_segment.angle

def distance_filter(entities, position, distance):
    with measure("Shapely & pygeodesi distance filtering"):
        res_entities = []
        shapely_point = to_shapely_point(position)
        for entity in entities:
            closest = closest_point_to(shapely_point, entity.geometry)
            closest_latlon = to_latlon(closest)
            cur_distance = distance_between(closest_latlon, position)
            if cur_distance <= distance:
                res_entities.append(entity)
        return res_entities
def effective_width_filter(entities, position):
    with measure("Shapely & pygeodesi effective distance filtering"):
        res_entities = []
        shapely_point = to_shapely_point(position)
        for entity in entities:
            if not entity.effective_width:
                continue
            closest = closest_point_to(shapely_point, entity.geometry)
            closest_latlon = to_latlon(closest)
            cur_distance = distance_between(closest_latlon, position)
            if cur_distance <= entity.effective_width:
                res_entities.append(entity)
        return res_entities

def calculate_absolute_distances(segments, entity):
    """Calculates how far could the entity based on its position trawel along the line represented by the segments in both directions, e. g. to the start or the end points of the whole line. Assumes that the closest segment calculation has already been done, e. g. that the LineSegment.current property is set correctly."""
    from_start = 0
    to_end = 0
    seen_current = False
    for segment in segments:
        if not segment.current:
            segment.calculate_length()
            if not seen_current:
                from_start += segment.length
            else:
                to_end += segment.length
        else:
            seen_current = True
            line_point = entity.closest_point_to(segment.line, False)
            from_start += distance_between(to_latlon(segment.start), line_point)
            to_end += distance_between(line_point, to_latlon(segment.end))
    return from_start, to_end

def opposite_turn_angle(angle):
    if angle < 0:
        return angle + 180
    else:
        return -(180 - angle)
    
def ensure_turn_angle_positive(turn_angle):
    if turn_angle < 0:
        return turn_angle + 360
    else:
        return turn_angle

def get_meaningful_turns(new_road, entity):
    """Returns the meaningful turns which could the given entity perform if you want to continue along the given road. Returns a list of tuples in the form (direction_description, formatted_distance, direction_change)."""
    from .humanization_utils import format_number, describe_angle_as_turn_instructions
    # These two imports are only needed in this function, so no point of doing them globally and complicating everything.
    from .services import config
    new_segments = merge_similar_line_segments(get_line_segments(wkb.loads(new_road.geometry)), config().presentation.angle_decimal_places)
    closest_new_segment = find_closest_line_segment_of(new_segments, entity.position_point)
    closest_new_segment.calculate_angle()
    required_angle_difference = closest_new_segment.angle - entity.direction
    from_start, to_end = calculate_absolute_distances(new_segments, entity)
    meaningful_directions = []
    if from_start > 10:
        meaningful_directions.append((describe_angle_as_turn_instructions(ensure_turn_angle_positive(opposite_turn_angle(required_angle_difference)), config().presentation.angle_decimal_places), format_number(from_start, config().presentation.distance_decimal_places), opposite_turn_angle(required_angle_difference)))
    if to_end > 10:
        meaningful_directions.append((describe_angle_as_turn_instructions(ensure_turn_angle_positive(required_angle_difference), config().presentation.angle_decimal_places), format_number(to_end, config().presentation.distance_decimal_places), required_angle_difference))
    return meaningful_directions
        