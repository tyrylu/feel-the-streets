from .generator import Generator
from shared.models import Road

class RoadGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Road)
        self.renames("highway", "type")
        self.renames("junction", "junction_type")
        self.renames("bicycle", "bicycle_allowed")
        self.renames("horse", "horse_allowed")
        self.renames("motor_vehicle", "motor_vehicle_allowed")
        self.renames("lanes:forward", "forward_lanes")
        self.renames("lanes:backward", "backward_lanes")
        self.renames("destination:lanes", "lane_destinations")
        self.renames("footway", "footway_type")
        self.renames("inline_skates", "inline_skates_allowed")
        self.renames("cycleway:left", "left_cycleway")
        self.renames("cycleway:right", "right_cycleway")
        self.renames("maxspeed:hgv", "maxspeed_hgv")
        self.renames("maxspeed:forward", "maxspeed_forward")
        self.renames("maxspeed:backward", "maxspeed_backward")
        self.renames("oneway:bicycle", "bicycle_oneway")
        self.renames("vehicle", "vehicle_allowed")
        self.renames("dog", "dogs_allowed")
        self.renames("motorcycle", "motorcycle_allowed")
        self.renames("bridge:structure", "bridge_structure")
        self.renames("oneway:tram", "tram_oneway")
        self.renames("direction", "incline")
        self.renames("FIXME", "fixme")
        self.renames("destination:symbol", "destination_symbol")
        self.removes("mtb", True)
        self.removes("bad_source:old:uhul:ortofoto")
        self.removes("motorroad")
        self.removes("veh_ban_until")
        self.removes("vehicle:conditional")
        self.removes("history")
        self.removes("hgv:conditional")
        self.removes("construction")
        self.removes("mtb")
        self.removes_subtree("aerialway")
        self.removes_subtree("turn")
        self.removes_subtree("toll")
        self.removes_subtree("piste")
        self.removes_subtree("demolished")
        self.removes_subtree("maxweight")
        self.removes_subtree("colonnade")
        self.removes_subtree("access")
        self.removes_subtree("vehicle:backward")
        
        
    def _prepare_properties(self, entity_spec, props, record):
        if "access" in props and "@" in props["access"]: # We don't really need those finer details
            props["access"] = props["access"].split(" ")[0]
        if "incline" in props and props["incline"][0].isdigit():
            del props["incline"] # Think of a better way how to handle those
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return "highway" in props