import glob
import json
import os
import pendulum
from osm_db import AreaDatabase
from .services import config

def cache_response(name, response):
    with open(os.path.join(config().config_path, name), "w", encoding="utf-8") as fp:
        json.dump(response, fp)
            
def get_cached_response(name):
    cache_path = os.path.join(config().config_path, name)
    if not os.path.exists(cache_path):
        return None
    with open(cache_path, encoding="utf-8") as fp:
        return json.load(fp)
        
def get_local_area_ids():
    results = []
    # Somewhat hacky, but we need the storage root only there and the path generation logic does not care whether the area actually exists.
    areas_storage_path = os.path.dirname(AreaDatabase.path_for(12345, False))
    for db_file in glob.glob(os.path.join(areas_storage_path, "*.db")):
        results.append(int(os.path.basename(db_file).replace(".db", "")))
    return results
