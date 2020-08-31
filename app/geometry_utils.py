import logging
import shapely.wkb as wkb
import shapely.geometry as geometry
import pydantic
from pygeodesy.ellipsoidalVincenty import LatLon, VincentyError
from . import services
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
    line: geometry.linestring.LineString
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

def get_line_segments(line):
    x_coords, y_coords = line.coords.xy
    num_coords = len(x_coords) - 1 # Every segment must have two points, so for example, for two points we get one segment, for three segments we get two, etc.
    segments = []
    for segment in range(num_coords):
        x1, y1 = x_coords[segment], y_coords[segment]
        x2, y2 = x_coords[segment + 1], y_coords[segment + 1]
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
