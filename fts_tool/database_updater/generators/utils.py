import logging
import json
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
    args["country"] = props.pop("addr:country", None)
    args["place"] = props.pop("addr:place", None)    
    args["city"] = props.pop("addr:city", None)
    args["post_code"]  = props.pop("addr:postcode", None)
    if isinstance(args["post_code"], str):
        args["post_code"] = args["post_code"].replace(" ", "") # We don't want the spaces in the canonical format.
        args["post_code"] = args["post_code"].replace("Brno-KrálovoPole", "") # And this string as well
        if not args["post_code"].isdigit():
            log.warn("Despite all tries, the post code sanitization failed for post code %s.", args["post_code"])
            del args["post_code"]
    args["conscription_number"] = props.pop("addr:conscriptionnumber", None)
    args["house_number"] = props.pop("addr:housenumber", None)
    args["street_number"] = props.pop("addr:streetnumber", None)
    args["street"] = props.pop("addr:street", None)
    args["provisional_number"] = props.pop("addr:provisionalnumber", None)
    args["suburb"] = props.pop("addr:suburb", None)
    args["house_name"] = props.pop("addr:housename", None)
    args = {k: v for k, v in args.items() if v}
    if "conscription_number" in args and ";" in args["conscription_number"]:
        log.warn("Semicolon in an address conscription number of address %s.", args)
        del args["conscription_number"]
    if "provisional_number" in args and ";" in args["provisional_number"]:
        log.warn("Semicolon in an address provisional number of address %s.", args)
        del args["provisional_number"]
    try:
        int(args.get("conscription_number", 0))
    except ValueError:
        log.warn("Non integral conscription number %s.", args["conscription_number"])
        del args["conscription_number"]
    if args:
        return args
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
