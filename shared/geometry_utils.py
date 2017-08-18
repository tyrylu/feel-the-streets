import logging
import attr
import shapely.geometry as geometry
from geodesy.ellipsoidalVincenty import LatLon, VincentyError

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

@attr.s
class LineSegment:
    line = attr.ib()
    start = attr.ib()
    end = attr.ib()
    length = attr.ib(default=None, init=False)
    angle = attr.ib(default=None, init=False)
    end_angle = attr.ib(default=None, init=False)
    current = attr.ib(default=False)

    def calculate_length(self):
        self.length = distance_between(to_latlon(self.start), to_latlon(self.end))

    def calculate_angle(self):
        self.angle, self.end_angle = bearings_to(to_latlon(self.start), to_latlon(self.end))

def get_line_segments(line):
    x_coords, y_coords = line.coords.xy
    num_coords = len(x_coords)
    segments = []
    for segment in range(num_coords):
        x1, y1 = x_coords[segment], y_coords[segment]
        x2, y2 = x_coords[(segment + 1)%num_coords], y_coords[(segment + 1)%num_coords]
        line_segment = geometry.linestring.LineString([(x1, y1),(x2, y2)])
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

def perpendicular_points(latlon, width, angle):
    left = latlon.destination(width/2, (angle - 90)%360)
    right = latlon.destination(width/2, (angle + 90)%360)
    return left, right
def create_containment_polygon_old(line, width):
    left_vertices = []
    right_vertices = []
    first = True
    for segment in get_line_segments(line):
        segment.calculate_angle()
        start_latlon = to_latlon(segment.start)
        end_latlon = to_latlon(segment.end)
        if first:
            first = False
            left, right = perpendicular_points(start_latlon, width, segment.angle)
            left_vertices.append((left.lon, left.lat))
            right_vertices.append((right.lon, right.lat))
        left, right = perpendicular_points(end_latlon, width, segment.end_angle)
        left_vertices.append((left.lon, left.lat))
        right_vertices.append((right.lon, right.lat))
    vertices = left_vertices
    vertices.extend(reversed(right_vertices))
    vertices.append(vertices[0])
    for idx, seg in enumerate(get_line_segments(line)):
        lp1, lp2 = vertices[idx], vertices[idx + 1]
        rp1, rp2 = vertices[-2 - idx - 1], vertices[-2 - idx]
        left = LineSegment(start=geometry.point.Point(lp1), end=geometry.point.Point(lp2), line=geometry.linestring.LineString((lp1, lp2)))
        right = LineSegment(start=geometry.point.Point(rp1), end=geometry.point.Point(rp2), line=geometry.linestring.LineString((rp1, rp2)))
        seg.calculate_angle()
        seg.calculate_length()
        left.calculate_angle()
        left.calculate_length()
        right.calculate_angle()
        right.calculate_length()
        log.debug(f"Checking line segment {idx}...")
        if not (seg.angle == left.angle == 180 - right.angle):
            log.debug(f"Angle mismatch: segment - left side: {seg.angle - left.angle}, segment - right side: {seg.angle - (180 -right.angle)}")
            log.debug(f"Segment angle difference: {seg.end_angle - seg.angle}")
        if not (seg.length == left.length == right.length):
            log.debug(f"Length mismatch: segment - left side: {seg.length - left.length}, segment - righ side: {seg.length - right.length}")
    return geometry.polygon.Polygon(vertices)
    
def create_containment_polygon(line, width):
    left_vertices = []
    right_vertices = []
    first = True
    last_left = None
    last_right = None
    for segment in get_line_segments(line):
        segment.calculate_angle()
        segment.calculate_length()
        start_latlon = to_latlon(segment.start)
        end_latlon = to_latlon(segment.end)
        if first:
            first = False
            last_left, last_right = perpendicular_points(start_latlon, width, segment.angle)
            left_vertices.append((last_left.lon, last_left.lat))
            right_vertices.append((last_right.lon, last_right.lat))
        last_left = last_left.destination(segment.length, segment.angle)
        last_right = last_right.destination(segment.length, segment.angle)
        left_vertices.append((last_left.lon, last_left.lat))
        right_vertices.append((last_right.lon, last_right.lat))
    vertices = left_vertices
    vertices.extend(reversed(right_vertices))
    vertices.append(vertices[0])
    for idx, seg in enumerate(get_line_segments(line)):
        lp1, lp2 = vertices[idx], vertices[idx + 1]
        rp1, rp2 = vertices[-2 - idx], vertices[-2 - idx - 1]
        left = LineSegment(start=geometry.point.Point(lp1), end=geometry.point.Point(lp2), line=geometry.linestring.LineString((lp1, lp2)))
        right = LineSegment(start=geometry.point.Point(rp1), end=geometry.point.Point(rp2), line=geometry.linestring.LineString((rp1, rp2)))
        seg.calculate_angle()
        seg.calculate_length()
        left.calculate_angle()
        left.calculate_length()
        right.calculate_angle()
        right.calculate_length()
        log.debug(f"Checking line segment {idx}...")
        left_dist = to_latlon(seg.start).distanceTo(to_latlon(left.start))
        right_dist = to_latlon(seg.start).distanceTo(to_latlon(right.start))
        left_end_dist = to_latlon(seg.end).distanceTo(to_latlon(left.end))
        right_end_dist = to_latlon(seg.end).distanceTo(to_latlon(right.end))
        if not (left_dist == right_dist == width/2):
            log.debug(f"Width mismatch: segment to left: {left_dist}, segment to right: {right_dist}")
        if not (left_end_dist == right_end_dist == width/2):
            log.debug(f"End width mismatch: segment to left: {left_end_dist}, segment to right: {right_end_dist}")
        if not (seg.angle == left.angle == 180 - right.angle):
            log.debug(f"Angle mismatch: segment - left side: {seg.angle - left.angle}, segment - right side: {seg.angle - (180 -right.angle)}")
            log.debug(f"Segment angle difference: {seg.end_angle - seg.angle}")
        if not (seg.length == left.length == right.length):
            log.debug(f"Length mismatch: segment - left side: {seg.length - left.length}, segment - righ side: {seg.length - right.length}")
    return geometry.polygon.Polygon(vertices)