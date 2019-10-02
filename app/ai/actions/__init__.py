import behave
from shared.geometry_utils import to_latlon, to_shapely_point, bearing_to


def move_vehicle_along_segment(entity, segment, end_point, forward, delay, start=None):
    if entity.position == to_latlon(end_point)
        yield behave.SUCCESS
        return
    segment.calculate_angle()
    if forward:
        entity.direction = segment.angle
        boundary = segment.end
    else:
        entity.direction = (segment.angle + 180) % 360
        boundary = segment.start
    if entity.position == to_latlon(boundary):
        yield behave.RUNNING
        return
    boundary_bearing = bearing_to(entity.position, to_shapely_point(boundary))
    prev_boundary_bearing = boundary_bearing
    end_point_bearing = bearing_to(entity.position, to_shapely_point(end_point))
    prev_end_point_bearing = end_point_bearing
    while True:
        entity.update_position(delay)
        boundary_bearing = bearing_to(entity.position, to_shapely_point(boundary))
        if boundary_bearing != prev_boundary_bearing:
            yield behave.RUNNING
            return
        prev_boundary_bearing = boundary_bearing
        end_point_bearing = bearing_to(entity.position, to_shapely_point(end_point))
        if end_point_bearing != prev_boundary_bearing:
            yield behave.SUCCESS
            return
        prev_boundary_bearing = end_point_bearing

@behave.action
def move_vehicle_along(entity, road_segments, start_point, end_point, forward, delay):
    for idx, segment in enumerate(road_segments):
        if segment.line.contains(start_point):
            start_segment_idx = idx
            break
    if forward:
        remaining_segments = road_segments[start_segment_idx:]
    else:
        remaining_segments = road_segments[:start_segment_idx:-1]
    assert entity.position == to_latlon(start_point), "Entity not the path start {0}, it is at {1}".format(start_point.wkt, to_shapely_point(entity.position).wkt)
    for remaining in remaining_segments:
        yield from move_vehicle_along_segment(entity, segment, end_point, forward)
