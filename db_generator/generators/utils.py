import logging
import json
from shared.models.address import Address
from geoalchemy import WKTSpatialElement

log = logging.getLogger(__name__)
polygon_features = json.load(open("polygon_features.json"))

def rename_dict_key(dct, old_names, new_name):
    if not isinstance(old_names, list):
        old_names = [old_names]
    for old_name in old_names:
        if old_name in dct:
            dct[new_name] = dct[old_name]
            del dct[old_name]
            break
    return dct
def create_address(props):
    args = {}
    props.pop("addr:country", None)
    args["place"] = props.pop("addr:place", None)    
    args["city"] = props.pop("addr:city", None)
    args["post_code"]  = props.pop("addr:postcode", None)
    if isinstance(args["post_code"], str):
        args["post_code"] = args["post_code"].replace(" ", "") # We don't want the spaces in the canonical format.
    args["conscription_number"] = props.pop("addr:conscriptionnumber", None)
    args["house_number"] = props.pop("addr:housenumber", None)
    args["street_number"] = props.pop("addr:streetnumber", None)
    args["street"] = props.pop("addr:street", None)
    args["provisional_number"] = props.pop("addr:provisionalnumber", None)
    args["suburb"] = props.pop("addr:suburb", None)
    args["house_name"] = props.pop("addr:housename", None)
    addr = Address(**args)
    if addr:
        return addr
    else:
        return None

def remove_subproperties(props, property):
    removable = []
    for key in props.keys():
        if key.startswith("%s:"%property):
            removable.append(key)
    for key in removable:
        log.debug("Removed key value pair %s=%s.", key, props[key])
        del props[key]
    return props

def unprefix_properties(props, prefix):
    changes = []
    for key in props.keys():
        if key.startswith("%s:"%prefix):
            new_name = ":".join(key.split(":")[1:])
            log.debug("Renaming %s to %s.", key, new_name)
            changes.append((key, new_name))
    for change in changes:
        rename_dict_key(props, change[0], change[1])
    return props

def should_be_closed(entity):
    for spec in polygon_features:
        if spec["key"] in entity["properties"]:
            if spec["polygon"] == "all":
                return True
            elif spec["polygon"] == "blacklist":
                if entity["properties"][spec["key"]] in spec["values"]:
                    return False
            elif spec["polygon"] == "whitelist":
                if entity["properties"][spec["key"]] in spec["values"]:
                    return True
            else:
                raise ValueError("Unknown polygon condition %s."%spec["polygon"])
    return False

def convert_coords(coords):
    if isinstance(coords[0], float):
        return "%s %s"%(coords[0], coords[1])
    else:
        coords = ["%s %s"%(coord[0], coord[1]) for coord in coords]
        return ", ".join(coords)

def ensure_closed(coords):
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords

def create_geometry(entity):
    spec = entity["geometry"]
    type = spec["type"]
    coords = convert_coords(spec["coordinates"])
    if type == "LineString":
        # The polygon object conditions are taken from:
        # https://wiki.openstreetmap.org/wiki/Overpass_turbo/Polygon_Features
        if should_be_closed(entity) and len(spec["coordinates"]) > 2:
            coords = convert_coords(ensure_closed(spec["coordinates"]))
            return WKTSpatialElement("POLYGON((%s))"%coords)
        else:
            return WKTSpatialElement("LINESTRING(%s)"%coords)
    elif type == "Point":
        return WKTSpatialElement("POINT(%s)"%coords)
    else:
        raise NotImplementedError("Unknown geometry type: %s"%spec)