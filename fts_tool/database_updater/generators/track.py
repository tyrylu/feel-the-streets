from .road import RoadGenerator
from shared.models import Track

class TrackGenerator(RoadGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Track)
        self.renames("motorcar", "motorcar_allowed")
        self.renames("mtb:scale:uphill", "mtb_scale_uphill")
        self.renames("mtb:scale:uphill", "mtb_scale_uphill")
        self.renames("leisure", "type")
        self.renames("bicycle:class", "bicycle_class")
        self.renames("ticks:description", "ticks_description")
        self.renames("motor_vehicle:note", "motor_vehicle_note")
        self.renames("survey:date", "survey_date")


        self.renames("proposed:segregated", "proposed_segregated")
        self.renames("incline:steep", "steep_incline")
        self.renames("lanes:sprint", "sprint_lanes")
    def _prepare_properties(self, entity_spec, props, record):
        if "area" in props and props["area"] == "no": # Can someone explain the thinking behind this to me?
            del props["area"]
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return (RoadGenerator.accepts(props) and (props["highway"] == "track") or "leisure" in props and props["leisure"] == "track") or "tracktype" in props
