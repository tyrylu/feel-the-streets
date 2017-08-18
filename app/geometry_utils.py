import shapely.wkt as wkt
from shared.geometry_utils import *
from . import services

def closest_point_to(point, db_geom):
    geom = wkt.loads(services.map()._db.scalar(db_geom.wkt))
    if isinstance(geom, geometry.point.Point):
        return geom
    elif isinstance(geom, geometry.linestring.LineString):
        return geom.interpolate(geom.project(point))
    elif isinstance(geom, geometry.polygon.Polygon):
        return geom.exterior.interpolate(geom.exterior.project(point))

def get_road_section_angle(pov, road):
    pov_point = to_shapely_point(pov.position)
    road_line = road.get_original_shapely_geometry(services.map()._db)
    closest_segment = get_closest_line_segment(pov_point, road_line)
    closest_segment.calculate_angle()
    return closest_segment.angle