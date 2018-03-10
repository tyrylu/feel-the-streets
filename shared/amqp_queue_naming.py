import hashlib

def get_client_queue_name(client_id: str, area_name: str) -> str:
    hashable = "{0}{1}".format(client_id, area_name).encode("UTF-8")
    return hashlib.new("sha3_256", hashable).hexdigest()