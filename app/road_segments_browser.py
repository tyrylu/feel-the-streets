from PySide6.QtWidgets import QDialog, QListWidget, QPushButton, QLabel, QVBoxLayout
from .geometry_utils import get_line_segments, find_closest_line_segment_of, to_latlon, distance_between, merge_similar_line_segments, get_complete_road_line
from .humanization_utils import format_number
from .services import config

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
        line = get_complete_road_line(road)
        segments = get_line_segments(line)
        segments = merge_similar_line_segments(segments, config().presentation.angle_decimal_places)
        current_idx = None
        for idx, segment in enumerate(segments):
            segment.calculate_angle()
            segment.calculate_length()
            segment_length = format_number(segment.length, config().presentation.distance_decimal_places)
            segment_angle = format_number(segment.angle, config().presentation.angle_decimal_places)
            if not segment.current:
                message = _("{distance} meters in angle {angle}°").format(distance=segment_length, angle=segment_angle)
            else:
                segment_latlon = person.closest_point_to(segment.line, False)
                middle_distance = distance_between(person.position, segment_latlon)
                start_distance = distance_between(to_latlon(segment.start), segment_latlon)
                start_distance = format_number(start_distance, config().presentation.distance_decimal_places)
                middle_distance = format_number(middle_distance, config().presentation.distance_decimal_places)
                message = _("{start_distance} meters of {distance} meters in angle {angle}° distant from road center by {middle_distance}").format(start_distance=start_distance, distance=segment_length, angle=segment_angle, middle_distance=middle_distance)
            segments_list.addItem(message)
            if segment.current:
                current_idx = idx
        if current_idx is not None:
            segments_list.setCurrentRow(current_idx)