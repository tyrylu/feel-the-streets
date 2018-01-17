import shapely.wkb as wkb
from shared.geometry_utils import *
from . import services

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
        geom = wkb.loads(geom.desc.desc)
    if geom.geom_type == "Point":
        return geom
    elif geom.geom_type == "LineString":
        return geom.interpolate(geom.project(point))
    elif geom.geom_type == "Polygon":
        return geom.exterior.interpolate(geom.exterior.project(point))
    elif geom.geom_type == "GeometryCollection":
        return closest_point_from_geoms(geom.geoms, point)
    else:
        raise RuntimeError("Can not process geometry of type %s."%geom.geom_type)

def get_road_section_angle(pov, road):
    pov_point = to_shapely_point(pov.position)
    road_line = road.get_original_shapely_geometry(services.map()._db)
    closest_segment = get_closest_line_segment(pov_point, road_line)
    closest_segment.calculate_angle()
    return closest_segment.angle