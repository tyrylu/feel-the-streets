import hashlib

def get_client_queue_name(client_id: str, area_osm_id: int) -> str:
    hashable = "{0}{1}".format(client_id, area_osm_id).encode("UTF-8")
    return hashlib.new("sha3_256", hashable).hexdigest()