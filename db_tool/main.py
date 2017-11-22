import json
import logging
import sys
from .log_aggregation import AggregatingFileHandler
import inspect
import overpass
from geoalchemy import WKTSpatialElement
import geoalchemy.functions as gf
from shared import Database
from shared.geometry_utils import create_containment_polygon
from . import generators
from .generators.generator import Generator
from .utils import get_srid_from_point
from .generation_record import GenerationRecord

log = logging.getLogger(__name__)

def maybe_polygonize(entity, db):
    if hasattr(entity, "effective_width") and entity.effective_width > 0 and db.scalar(gf.geometry_type(entity.geometry)) == "LINESTRING":
        entity.original_geometry = entity.geometry
        log.debug(f"Creating containment polygon for entity {entity.id}.")
        x = db.scalar(entity.original_geometry.point_n(1).x())
        y = db.scalar(entity.original_geometry.point_n(1).y())
        entity.geometry = db.scalar(entity.original_geometry.transform(get_srid_from_point(x, y)).buffer(entity.effective_width).transform(4326).wkt())
    return entity

def interpret_entity(entity, is_way, record):
    for member in generators.__dict__.values():
        if not inspect.isclass(member) or not issubclass(member, Generator):
            continue
        if member.accepts(entity["properties"]):
            log.debug("%s accepted properties.", member.__name__)
            instance = member()
            return instance.generate_from(entity, is_way, record)
    raise ValueError("No generator accepted properties: %s."%entity["properties"])

def interpret(query, api, db, is_way, record):
    log.info("Interpreting entities returned by query %s...", query)
    res = api.Get(query)
    if "--save-raw" in sys.argv:
        query = query.replace('"', "'")
        fp = open(query, "w", encoding="utf-8")
        fp.write(json.dumps(res))
        fp.close()
    log.info("Interpreting the results and storing them in the database...")
    total = len(res["features"])
    record.total_entities += total
    for entity_dict in res["features"]:
        entity = interpret_entity(entity_dict, is_way, record)
        if entity is None:
            continue # No semantic meaning
        record.processed_entities += 1
        db.add(entity)
        entity = maybe_polygonize(entity, db)
    db.commit()

def main():
    location = input("Location name: ")
    logging.basicConfig(level=logging.INFO, handlers=[AggregatingFileHandler("db_generation_%s.log"%location, "w", "UTF-8")])
    api = overpass.API(timeout=60)
    db = Database(location)
    db.create()
    record = GenerationRecord()
    interpret('area["name"="%s"];node(area);'%location, api, db, False, record)
    print("Nodes done.")
    interpret('area["name"="%s"];way(area);'%location, api, db, True, record)
    db.commit()
    record.save_to_file("generation_record_%s.txt"%location)
    input("Okay.")
