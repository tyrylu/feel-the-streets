from collections import defaultdict
import logging
from typing import Optional
from osm_db import (
    Geometry,
    geodesic_distance,
    geodesic_bearing,
    geodesic_distance_and_bearings,
    geodesic_destination,
)
import pydantic
from .latlon import LatLon
from .measuring import measure

log = logging.getLogger(__name__)

def to_latlon(xy_tuple):
    """Convert a (x, y) / (lon, lat) coordinate tuple to a LatLon."""
    return LatLon(xy_tuple[1], xy_tuple[0])

def distance_between(point1, point2):
    try:
        return geodesic_distance(point1.lat, point1.lon, point2.lat, point2.lon)
    except Exception:
        return 0

def bearing_to(initial, target):
    try:
        return geodesic_bearing(initial.lat, initial.lon, target.lat, target.lon)
    except Exception:
        return 0

def bearings_to(initial, target):
    try:
        dist, initial_bearing, final_bearing = geodesic_distance_and_bearings(
            initial.lat, initial.lon, target.lat, target.lon
        )
        return initial_bearing, final_bearing
    except Exception:
        return 0, 0

class LineSegment(pydantic.BaseModel):
    line: Geometry
    start: tuple
    end: tuple
    length: Optional[float] = None
    angle: Optional[float] = None
    end_angle: Optional[float] = None
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
            current_segment = LineSegment(start=current_segment.start, end=segment.end, line=Geometry.from_linestring([current_segment.line.coords()[0], segment.line.coords()[1]]))
        else:
            merged.append(current_segment)
            current_segment = segment
            current_angle = round(current_segment.angle, precision)
    merged.append(current_segment) # We must add this one manually because it did not have time to be replaced by another one
    return merged

def get_line_segments(line):
    coords = line.coords()
    num_coords = len(coords) - 1 # Every segment must have two points, so for example, for two points we get one segment, for three segments we get two, etc.
    segments = []
    for segment in range(num_coords):
        x1, y1 = coords[segment]
        x2, y2 = coords[segment + 1]
        line_segment = Geometry.from_linestring([(x1, y1), (x2, y2)])
        segments.append(LineSegment(line=line_segment, start=(x1, y1), end=(x2, y2)))
    return segments

def find_closest_line_segment_of(segments, point):
    min_dist = 10**20
    best_segment: Optional[LineSegment] = None
    for line_segment in segments:
        dist = line_segment.line.euclidean_distance_to_point(point[0], point[1])
        if dist < min_dist:
            min_dist = dist
            best_segment = line_segment
    if not best_segment:
        raise ValueError("No best segment found.")
    best_segment.current = True
    return best_segment

def get_closest_line_segment(point, line):
    return find_closest_line_segment_of(get_line_segments(line), point)

def xy_ranges_bounding_square(center_latlon, side):
    # First, get the x bounds
    side1_lat, side1_lon = geodesic_destination(center_latlon.lat, center_latlon.lon, side/2, 0)
    edge1_lat, edge1_lon = geodesic_destination(side1_lat, side1_lon, side/2, 270)
    min_x = edge1_lon
    max_y = edge1_lat
    _edge2_lat, edge2_lon = geodesic_destination(side1_lat, side1_lon, side/2, 90)
    max_x = edge2_lon
    edge3_lat, _edge3_lon = geodesic_destination(edge1_lat, edge2_lon, side, 180)
    min_y = edge3_lat
    # Note that if the square would be positioned just right, the max/min invariants would not hold, but for the foreseeable future usages it should be okay.
    return min_x, min_y, max_x, max_y

def closest_point_from_geoms(geoms, point):
    min_dist = float("inf")
    min_point = None
    for geom in geoms:
        geom_point = closest_point_to(point, geom, convert=False)
        dist = geom.euclidean_distance_to_point(geom_point[0], geom_point[1])
        if dist < min_dist:
            min_dist = dist
            min_point = geom_point
    return min_point

def closest_point_to(point, geom, convert=True):
    # If geom is raw bytes (geometry_bytes), parse via Geometry — but with the new API,
    # entity.geometry already returns a Geometry object, so convert=True is kept for
    # backwards compatibility with any remaining bytes usage.
    if convert and not isinstance(geom, Geometry):
        raise TypeError("Expected a Geometry object; raw bytes are no longer supported here")
    geom_type = geom.geom_type()
    if geom_type == "Point":
        return geom.point_coords()
    elif geom_type in {"LineString", "MultiLineString", "GeometryCollection", "MultiPolygon"}:
        return geom.closest_point(point[0], point[1])
    elif geom_type == "Polygon":
        return geom.closest_point(point[0], point[1])
    else:
        raise RuntimeError("Can not process geometry of type %s." % geom_type)

def get_road_section_angle(pov, road):
    pov_point = (pov.position.lon, pov.position.lat)
    road_line = road.geometry
    closest_segment = get_closest_line_segment(pov_point, road_line)
    closest_segment.calculate_angle()
    return closest_segment.angle

def distance_filter(entities, position, distance):
    with measure("Geometry distance filtering"):
        res_entities = []
        point = (position.lon, position.lat)
        for entity in entities:
            closest = closest_point_to(point, entity.geometry)
            closest_latlon = to_latlon(closest)
            cur_distance = distance_between(closest_latlon, position)
            if cur_distance <= distance:
                res_entities.append(entity)
        return res_entities

def effective_width_filter(entities, position):
    with measure("Geometry effective distance filtering"):
        res_entities = []
        point = (position.lon, position.lat)
        for entity in entities:
            if not entity.effective_width:
                continue
            closest = closest_point_to(point, entity.geometry)
            closest_latlon = to_latlon(closest)
            cur_distance = distance_between(closest_latlon, position)
            if cur_distance <= entity.effective_width / 2:
                res_entities.append(entity)
        return res_entities

def canonicalize_line(line):
    """Ensures a consistent order of a line's coordinates."""
    coords = line.coords()
    coord1 = to_latlon(coords[0])
    coord2 = to_latlon(coords[1])
    if bearing_to(coord1, coord2) > 180:
        return Geometry.from_linestring(list(reversed(coords)))
    else:
        return line

def xy_tuple_to_latlon(xy_tuple):
    return LatLon(xy_tuple[1], xy_tuple[0])

def line_segment_part_bearing(linestring, starting_segment_index):
    coords = linestring.coords()
    return bearing_to(xy_tuple_to_latlon(coords[starting_segment_index]), xy_tuple_to_latlon(coords[starting_segment_index + 1]))

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
    closest_diff = abs(base_bearing - line_segment_part_bearing(merge_candidates[0], candidate_index))
    closest_candidate = merge_candidates[0]
    for candidate in merge_candidates[1:]:
        bearing = line_segment_part_bearing(candidate, candidate_index)
        diff = abs(base_bearing - bearing)
        if diff < closest_diff:
            closest_diff = diff
            closest_candidate = candidate
    return closest_candidate

def get_complete_road_line(road):
    from .services import map
    road_line = road.geometry
    road_name = road.value_of_field("name")
    if not road_name:
        return road_line
    if road_line.is_closed():
        return road_line
    other_road_parts = map().get_entities_named(road_name)
    other_road_parts = [part for part in other_road_parts if part.id != road.id and part.is_road_like]
    lines = [part.geometry for part in other_road_parts]
    lines = [l for l in lines if l.geom_type() == "LineString" and not l.is_closed()]
    if not lines:
        return road_line
    lines.append(road_line)
    start_points = defaultdict(list)
    end_points = defaultdict(list)
    to_check = []
    results = []
    for line in lines:
        line = canonicalize_line(line)
        coords = line.coords()
        start_points[coords[0]].append(line)
        end_points[coords[-1]].append(line)
        to_check.append(line)
    while to_check:
        candidate = to_check.pop()
        candidate_coords = candidate.coords()
        begins_with_lines = end_points.get(candidate_coords[0])
        continues_with_lines = start_points.get(candidate_coords[-1])
        if begins_with_lines or continues_with_lines:
            start_points[candidate_coords[0]].remove(candidate)
            end_points[candidate_coords[-1]].remove(candidate)
        if begins_with_lines:
            begins_with = select_mergeable_line(candidate, begins_with_lines, merge_at_end=False)
            to_check.remove(begins_with)
            bw_coords = begins_with.coords()
            end_points[bw_coords[-1]].remove(begins_with)
            start_points[bw_coords[0]].remove(begins_with)
            merged = Geometry.from_linestring(list(bw_coords) + list(candidate_coords[1:]))
            merged_coords = merged.coords()
            start_points[merged_coords[0]].append(merged)
            end_points[merged_coords[-1]].append(merged)
            to_check.append(merged)
        elif continues_with_lines:
            continues_with = select_mergeable_line(candidate, continues_with_lines, merge_at_end=True)
            to_check.remove(continues_with)
            cw_coords = continues_with.coords()
            start_points[cw_coords[0]].remove(continues_with)
            end_points[cw_coords[-1]].remove(continues_with)
            merged = Geometry.from_linestring(list(candidate_coords[:-1]) + list(cw_coords))
            merged_coords = merged.coords()
            start_points[merged_coords[0]].append(merged)
            end_points[merged_coords[-1]].append(merged)
            to_check.append(merged)
        else:
            start_points[candidate_coords[0]].remove(candidate)
            end_points[candidate_coords[-1]].remove(candidate)
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
    base_geom = base_road.geometry
    part_geom = known_crossing_part.geometry
    intersection = base_geom.intersection(part_geom)
    if intersection.is_empty():
        return None
    if intersection.geom_type() == "Point":
        return intersection
    # Did not find a point intersection so try to find one from the candidates, they might have simpler ones
    for candidate in candidates:
        candidate_geom = candidate.geometry
        candidate_intersection = base_geom.intersection(candidate_geom)
        if not candidate_intersection.is_empty() and intersection.euclidean_distance_to_point(*candidate_intersection.point_coords()) == 0.0 and candidate_intersection.geom_type() == "Point":
            return candidate_intersection
    log.warning("Did not find a point intersection for base road %s, known crossing part %s and candidates %s.", base_road.id, known_crossing_part.id, [c.id for c in candidates])
    return None
