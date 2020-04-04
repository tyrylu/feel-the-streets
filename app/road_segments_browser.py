from PySide2.QtWidgets import QDialog, QListWidget, QPushButton, QLabel, QVBoxLayout
import shapely.wkb as wkb
from .geometry_utils import get_line_segments, find_closest_line_segment_of, to_shapely_point, to_latlon, distance_between
from .services import map

class RoadSegmentsBrowserDialog(QDialog):
    
    def __init__(self, parent, person, road):
        super().__init__(parent)
        self.setWindowTitle(_("Road details"))
        layout = QVBoxLayout()
        segments_label = QLabel(_("Road segments"), self)
        layout.addWidget(segments_label)
        segments_list = QListWidget(self)
        segments_label.setBuddy(segments_list)
        segments_list.setAccessibleName(segments_label.text())
        layout.addWidget(segments_list)
        close_button = QPushButton(_("Close"), self)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        self.setLayout(layout)
        line = wkb.loads(road.geometry)
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
            segments_list.addItem(message)
            if segment.current:
                current_idx = idx
        segments_list.setCurrentRow(current_idx)