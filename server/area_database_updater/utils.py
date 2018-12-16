import shapely
import math
import json
import logging


log = logging.getLogger(__name__)
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

def coords_to_text(coords):
    return ", ".join("%s %s"%(coord[0], coord[1]) for coord in coords)

def _find_connectable_segments(segments):
    if len(segments) == 1:
        return None, None # Nothing to connect remains
    starts = {}
    ends = {}
    for segment in segments:
        starts[segment[0]] = segment
        ends[segment[-1]] = segment
    for end in ends.keys():
        if end in starts:
            return ends[end], starts[end]
    return None, None

def connect_polygon_segments(segments):
    while True:
        first, second = _find_connectable_segments(segments)
        if first is None:
            break
        segments.remove(second)
        first.extend(second[1:])
    for i, segment in enumerate(segments):
        segments[i] = ensure_closed(segment)
    return segments

def ensure_valid_geometry(geometry):
    if "EMPTY" in geometry:
        return None
    if geometry.startswith("POINT") or geometry.startswith("LINESTRING"):
        return geometry
    try:
        sh_geom = shapely.wkt.loads(geometry)
        if not sh_geom.is_valid:
            log.debug("Invalid geometry %s.", geometry)
            sh_geom = sh_geom.buffer(0)
            if not sh_geom.is_valid or "EMPTY" in sh_geom.wkt:
                log.error("Zero buffer failed to fix the entity geometry validity.")
                return None
    except Exception as exc:
        log.error("Failed to parse geometry %s, error %s.", geometry, exc)
        return None
    return sh_geom.wkt