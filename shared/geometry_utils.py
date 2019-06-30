import logging
import attr
import shapely.geometry as geometry
from pygeodesy.ellipsoidalVincenty import LatLon, VincentyError

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