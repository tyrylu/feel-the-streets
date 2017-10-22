import math
import json

def get_srid_from_point(x, y):
    if y < 0:
        base_srid = 32700
    else:
        base_srid = 32600
    return base_srid + math.floor((x+186)/6)

with open("polygon_features.json", "r") as fp:
    polygon_features = json.load(fp)    
def object_should_have_closed_geometry(object):
    for spec in polygon_features:
        if spec["key"] in object.tags:
            if spec["polygon"] == "all":
                return True
            elif spec["polygon"] == "blacklist":
                if object.tags[spec["key"]] in spec["values"]:
                    return False
            elif spec["polygon"] == "whitelist":
                if object.tags[spec["key"]] in spec["values"]:
                    return True
            else:
                raise ValueError("Unknown polygon condition %s."%spec["polygon"])
    return False

def ensure_closed(coords):
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords
