import wx
import wx.xrc as xrc
import shapely.wkt as wkt
from .geometry_utils import get_line_segments, find_closest_line_segment_of, to_shapely_point, to_latlon, distance_between
from .services import map

class RoadSegmentsBrowserDialog(wx.Dialog):
    xrc_name = "road_segments_browser"
    def post_init(self, person, road):
        self.EscapeId = xrc.XRCID("close")
        segments_list = self.FindWindowByName("segments")
        line = wkt.loads(road.geometry)
        segments = get_line_segments(line)
        closest = find_closest_line_segment_of(segments, to_shapely_point(person.position))
        current_idx = None
        for idx, segment in enumerate(segments):
            segment.calculate_angle()
            segment.calculate_length()
            if not segment.current:
                message = _("{distance:.2f} meters in angle {angle:.2f}°").format(distance=segment.length, angle=segment.angle)
            else:
                segment_point = segment.line.interpolate(segment.line.project(to_shapely_point(person.position)))
                segment_latlon = to_latlon(segment_point)
                middle_distance = distance_between(person.position, segment_latlon)
                start_distance = distance_between(to_latlon(segment.start), segment_latlon)
                message = _("{start_distance:.2f} meters of {distance:.2f} meters in angle {angle:.2f}° distant from road center by {middle_distance:.2f}").format(start_distance=start_distance, distance=segment.length, angle=segment.angle, middle_distance=middle_distance)
            segments_list.Append(message)
            if segment.current:
                current_idx = idx
        segments_list.Select(current_idx)