import shapely.wkt as wkt
from shared.geometry_utils import *
from . import services
from .measuring import measure

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
        geom = wkt.loads(geom)
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
    road_line = wkt.loads(road.geometry)
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
