import glob
import os
import pendulum
from osm_db import AreaDatabase
from .services import config

def cache_area_names(areas_response):
    with open(os.path.join(config().config_path, "area.names"), "w", encoding="utf-8") as fp:
        for area in areas_response:
            fp.write("{}={}\n".format(area["osm_id"], area["name"]))

def get_area_names_cache():
    names = {}
    cache_path = os.path.join(config().config_path, "area.names")
    if not os.path.exists(cache_path):
        return names
    with open(cache_path, encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            parts = line.split("=")
            names[int(parts[0])] = parts[1]
    return names

def get_local_area_infos():
    results = []
    # Somewhat hacky, but we need the storage root only there and the path generation logic does not care whether the area actually exists.
    areas_storage_path = os.path.dirname(AreaDatabase.path_for(12345, False))
    cache = get_area_names_cache()
    for db_file in glob.glob(os.path.join(areas_storage_path, "*.db")):
        info = os.stat(db_file)
        osm_id = int(os.path.basename(db_file).replace(".db", ""))
        name = cache.get(osm_id, str(osm_id))
        mtime = pendulum.from_timestamp(info.st_mtime).to_rfc3339_string()
        ctime = pendulum.from_timestamp(info.st_ctime).to_rfc3339_string()
        results.append({"osm_id": osm_id, "name":name, "updated_at": mtime, "state": "Local", "created_at": ctime, "db_size": info.st_size})
    return results
