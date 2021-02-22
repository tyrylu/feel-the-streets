from collections import defaultdict
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
    from .humanization_utils import describe_entity
    with measure("Shapely & pygeodesi effective distance filtering"):
        res_entities = []
        shapely_point = to_shapely_point(position)
        for entity in entities:
            if not entity.effective_width:
                continue
            closest = closest_point_to(shapely_point, entity.geometry)
            closest_latlon = to_latlon(closest)
            cur_distance = distance_between(closest_latlon, position)
            if cur_distance <= entity.effective_width / 2:
                res_entities.append(entity)
        return res_entities

def canonicalize_line(line):
    """Ensures a consistent order of a line's coordinates."""
    coord1 = LatLon(line.coords[0][1], line.coords[0][0])
    coord2 = LatLon(line.coords[1][1], line.coords[1][0])
    if bearing_to(coord1, coord2) > 180:
        return LineString(reversed(line.coords))
    else:
        return line

def xy_tuple_to_latlon(xy_tuple):
    return LatLon(xy_tuple[1], xy_tuple[0])

def line_segment_part_bearing(linestring, starting_segment_index):
    return bearing_to(xy_tuple_to_latlon(linestring.coords[starting_segment_index]), xy_tuple_to_latlon(linestring.coords[starting_segment_index + 1]))

def select_mergeable_line(merge_with, merge_candidates, merge_at_end):
    if len(merge_candidates) == 1:
        return merge_candidates[0]
    if merge_at_end:
        base_index = -2
        candidate_index = 0
    else:
        base_index = 0
        candidate_index = -2
    base_bearing = line_segment_part_bearing(merge_with, base_index)
    closest_diff = abs(base_bearing -line_segment_part_bearing(merge_candidates[0], candidate_index))
    closest_candidate = merge_candidates[0]
    for candidate in merge_candidates[1:]:
        bearing = line_segment_part_bearing(candidate, candidate_index)
        diff = abs(base_bearing -bearing)
        if diff < closest_diff:
            closest_diff = diff
            closest_candidate = candidate
    return closest_candidate

def get_complete_road_line(road):
    from .services import map
    road_line = wkb.loads(road.geometry)
    road_name = road.value_of_field("name")
    if not road_name:
        return road_line
    if road_line.is_closed:
        return road_line
    other_road_parts = map().get_entities_named(road_name)
    other_road_parts = [part for part in other_road_parts if part.id != road.id and part.is_road_like]
    lines = [wkb.loads(part.geometry) for part in other_road_parts]
    lines = [l for l in lines if l.geom_type == "LineString" and not l.is_closed]
    if not lines:
        return road_line
    lines.append(road_line)
    start_points = defaultdict(list)
    end_points = defaultdict(list)
    to_check = []
    results = []
    for line in lines:
        line = canonicalize_line(line)
        start_points[line.coords[0]].append(line)
        end_points[line.coords[-1]].append(line)
        to_check.append(line)
    i = 0
    while to_check:
        candidate = to_check.pop()
        begins_with_lines = end_points.get(candidate.coords[0])
        continues_with_lines = start_points.get(candidate.coords[-1])
        if begins_with_lines or continues_with_lines:
            start_points[candidate.coords[0]].remove(candidate)
            end_points[candidate.coords[-1]].remove(candidate)
        if begins_with_lines:
            begins_with = select_mergeable_line(candidate, begins_with_lines, merge_at_end=False)
            to_check.remove(begins_with)
            end_points[begins_with.coords[-1]].remove(begins_with)
            start_points[begins_with.coords[0]].remove(begins_with)
            merged = LineString(list(begins_with.coords) + list(candidate.coords[1:]))
            start_points[merged.coords[0]].append(merged)
            end_points[merged.coords[-1]].append(merged)
            to_check.append(merged)
        elif continues_with_lines:
            continues_with = select_mergeable_line(candidate, continues_with_lines, merge_at_end=True)
            to_check.remove(continues_with)
            start_points[continues_with.coords[0]].remove(continues_with)
            end_points[continues_with.coords[-1]].remove(continues_with)
            merged = LineString(list(candidate.coords[:-1]) + list(continues_with.coords))
            start_points[merged.coords[0]].append(merged)
            end_points[merged.coords[-1]].append(merged)
            to_check.append(merged)
        else:
            start_points[candidate.coords[0]].remove(candidate)
            end_points[candidate.coords[-1]].remove(candidate)
            results.append(candidate)
    for result in results:
        if result.contains(road_line):
            return result
    
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

def turn_angle_as_diff_from_zero(turn_angle):
    if turn_angle <= 180:
        return turn_angle
    else:
        return 360 - turn_angle

def get_meaningful_turns(new_road, entity, zero_turn_is_meaningful=False, ignore_length=False):
    """Returns the meaningful turns which could the given entity perform if you want to continue along the given road. Returns a list of tuples in the form (direction_description, formatted_distance, direction_change, road). Adding the road is done only because of the fact that the turn tuples are processed by functions lacking the selected road context, but the functions need it anyway."""
    # These two imports are only needed in this function, so no point of doing them globally and complicating everything.
    from .humanization_utils import format_number, describe_angle_as_turn_instructions
    from .services import config
    new_segments = merge_similar_line_segments(get_line_segments(get_complete_road_line(new_road)), config().presentation.angle_decimal_places)
    closest_new_segment = find_closest_line_segment_of(new_segments, entity.position_point)
    closest_new_segment.calculate_angle()
    required_angle_difference = closest_new_segment.angle - entity.direction
    from_start, to_end = calculate_absolute_distances(new_segments, entity)
    meaningful_directions = []
    if (ignore_length or from_start > 5) and (zero_turn_is_meaningful or abs(opposite_turn_angle(required_angle_difference)) != 0):
        meaningful_directions.append((describe_angle_as_turn_instructions(ensure_turn_angle_positive(opposite_turn_angle(required_angle_difference)), config().presentation.angle_decimal_places), format_number(from_start, config().presentation.distance_decimal_places), opposite_turn_angle(required_angle_difference), new_road))
    if (ignore_length or to_end > 5) and (zero_turn_is_meaningful or abs(required_angle_difference) != 0):
        meaningful_directions.append((describe_angle_as_turn_instructions(ensure_turn_angle_positive(required_angle_difference), config().presentation.angle_decimal_places), format_number(to_end, config().presentation.distance_decimal_places), required_angle_difference, new_road))
    return meaningful_directions
        
def get_smaller_turn(turn_choices):
    return min(turn_choices, key=lambda i: turn_angle_as_diff_from_zero(abs(i[2])))

def get_crossing_point(base_road, known_crossing_part, candidates):
    """Returns the point where the base_road intersects with the known_crossing_part. If that intersection is more complex, finds the correct point using the candidates as help."""
    base_geom = wkb.loads(base_road.geometry)
    part_geom = wkb.loads(known_crossing_part.geometry)
    intersection = base_geom.intersection(part_geom)
    if intersection.is_empty:
        return None
    if intersection.geom_type == "Point":
        return intersection
    # Did not find a point intersection so try to find one from the candidates, they might have simpler ones
    for candidate in candidates:
        candidate_geom = wkb.loads(candidate.geometry)
        candidate_intersection = base_geom.intersection(candidate_geom)
        if not  candidate_intersection.is_empty and intersection.distance(candidate_intersection) == 0.0 and candidate_intersection.geom_type == "Point":
            return candidate_intersection
    log.warn("Did not find a point intersection for base road %s, known crossing part %s and candidates %s.", base_road.id, known_crossing_part.id, [c.id for c in candidates])
    return None
