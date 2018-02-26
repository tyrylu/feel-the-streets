import time
import logging
import json
import os
import hashlib
import sys
import gzip
import requests
import xml.etree.ElementTree as et
import overpass
from shared.entities.enums import OSMObjectType
from .osm_object import OSMObject
from .osm_change import OSMObjectChange, OSMChangeType
from .utils import object_should_have_closed_geometry, ensure_closed, coords_to_text, connect_polygon_segments

log = logging.getLogger(__name__)
class OSMObjectManager:
    _query_template = "[out:json][timeout:{timeout}];{query};out meta;"
    _diff_template = "[out:xml][timeout:{timeout}][adiff:\"{after}\"];{query};out meta;"
    _retrieve_data_template = '((area["name"="{area}"];node(area);area["name"="{area}"];way(area);area["name"="{area}"];rel(area);>>);>>)'

    def __init__(self, use_cache, cache_responses):
        self._api = overpass.API(timeout=600)
        self._nodes = {}
        self._ways = {}
        self._rels = {}
        self._cache_responses = cache_responses
        self._use_cache = use_cache

    def lookup_objects_in(self, area):
        query = self._retrieve_data_template.format(area=area)
        objects = self._cache_results_of(query)
        self._ensure_has_cached_dependencies_for(objects)
        #self.lookup_nodes_in(area)
        #self.lookup_ways_in(area)
        #self.lookup_relations_in(area)

    def _cache_objects_of(self, response):
        log.info("Converting and caching results.")
        for osm_object in response["elements"]:
            dest = self._get_container_for_objects_of_type(osm_object.type)
            dest[osm_object.id] = osm_object
    
    def _run_query(self, query, timeout, is_lookup=True, format="json"):
        if self._use_cache:
            query_hash = hashlib.new("sha3_256", query.encode("UTF-8")).hexdigest()
            cache_path = os.path.join("query_cache", query_hash)
            if os.path.exists(cache_path):
                with gzip.open(cache_path, "rt", encoding="UTF-8") as fp:
                    log.debug("Returning cached query result.")
                    return json.load(fp)
        try:
            start = time.time()
            if is_lookup:
             raw_query = self._query_template.format(timeout=timeout, query=query)
            else:
                raw_query = query
            resp = self._api.Get(raw_query, build=False, responseformat=format)
            log.info("Query successful, duration %s seconds.", time.time() - start)
        except overpass.MultipleRequestsError:
            log.warn("Multiple requests, killing them despite not knowing what they are.")
            requests.get("http://overpass-api.de/api/kill_my_queries")
            return self._run_query(query, timeout)
        if self._cache_responses:
            query_hash = hashlib.new("sha3_256", query.encode("UTF-8")).hexdigest()
            if not os.path.exists("query_cache"):
                log.info("Creating query cache directory because it is needed.")
                os.mkdir("query_cache")
            with gzip.open(os.path.join("query_cache", query_hash), "wt", encoding="UTF-8") as fp:
                json.dump(resp, fp)
        log.debug("Returning live result from overpass-api.de.")
        return resp
        
    def _run_query_and_convert(self, query, timeout=900):
        resp = self._run_query(query, timeout)
        resp["elements"] = [OSMObject.from_dict(e) for e in resp["elements"] if e["type"] != "area"]
        return resp
    
    def _cache_results_of(self, query):
        log.debug("Caching results of query %s.", query)
        resp = self._run_query_and_convert(query)
        self._cache_objects_of(resp)
        return resp["elements"]

    def lookup_nodes_in(self, area):
        log.info("Looking for nodes in %s.", area)
        self._cache_results_of('area["name"="%s"];node(area)'%area)

    def lookup_ways_in(self, area):
        log.info("Looking for ways in %s.", area)
        objects = self._cache_results_of('area["name"="%s"];way(area)'%area)
        self._ensure_has_cached_dependencies_for(objects)

    def lookup_relations_in(self, area):
        log.info("Looking for relations in %s.", area)
        objects = self._cache_results_of('area["name"="%s"];rel(area)'%area)
        self._ensure_has_cached_dependencies_for(objects)

    def _get_container_for_objects_of_type(self, type):
        if type is OSMObjectType.node:
            return self._nodes
        elif type is OSMObjectType.way:
            return self._ways
        elif type is OSMObjectType.relation:
            return self._rels
        else:
            raise ValueError("Unknown OSM object type %s."%type)

    def _ensure_has_cached_dependencies_for(self, objects):
        missing = {OSMObjectType.node: [], OSMObjectType.way: [], OSMObjectType.relation: []}
        totals = {OSMObjectType.node: 0, OSMObjectType.way: 0, OSMObjectType.relation: 0}
        for object in objects:
            if object.type is OSMObjectType.node:
                continue # Nodes have no dependencies
            elif object.type is OSMObjectType.way:
                for node in object.nodes:
                    totals[OSMObjectType.node] += 1
                    if not self.has_object(OSMObjectType.node, node):
                        log.debug("Node %s missing.", node)
                        missing[OSMObjectType.node].append(node)
                    else:
                        log.debug("Node %s is not missing.", node)
            elif object.type is OSMObjectType.relation:
                for member in object.members:
                    totals[member.type] += 1
                    if not self.has_object(member.type, member.ref):
                        log.debug("%s %s missing.", member.type.name.upper(), member.ref)
                        missing[member.type].append(member.ref)
                    else:
                        log.debug("%s %s is not missing.", member.type.name.upper(), member.ref)
        for type, ids in missing.items():
            if totals[type]:
                log.info("Out of %s dependent %ss %s was missing.", totals[type], type.name, len(ids))
            if ids:
                self._lookup_objects(type, *ids)

    def has_object(self, type, id):
        return id in self._get_container_for_objects_of_type(type)

    def _lookup_objects(self, type, *ids):
        objects = self._cache_results_of("%s(id:%s)"%(type.name, ",".join(str(id) for id in ids)))
        self._ensure_has_cached_dependencies_for(objects)

    def get_object(self, type, id):
        if not self.has_object(type, id):
            self._lookup_objects(type, id)
        return self._get_container_for_objects_of_type(type)[id]

    def _enrich_tags(self, object, parent):
        object.tags["parent_osm_id"] = "{0}{1}".format(parent.type.name[0], parent.id)

    def related_objects_of(self, object):
        if object.type is OSMObjectType.node:
            return []
        elif object.type is OSMObjectType.way:
            self._ensure_has_cached_dependencies_for([object])
            for child_id in object.nodes:
                child = self.get_object(OSMObjectType.node, child_id)
                self._enrich_tags(child, object)
                yield child
        elif object.type is OSMObjectType.relation:
            self._ensure_has_cached_dependencies_for([object])
            for member in object.members:
                member_obj = self.get_object(member.type, member.ref)
                self._enrich_tags(member_obj, object)
                if member.role:
                    member_obj.tags["role"] = member.role
                yield member_obj

    def _get_way_coords(self, way):
        coords = []
        for related in self.related_objects_of(way):
            coords.append((related.lon, related.lat))
        return coords

    def get_geometry_as_wkt(self, object, close_lines_if_possible=False):
        if object.type is OSMObjectType.node:
            return "POINT(%s %s)"%(object.lon, object.lat)
        elif object.type is OSMObjectType.way:
            coords = self._get_way_coords(object)
            if close_lines_if_possible and len(coords) <= 2:
                return None
            if (object_should_have_closed_geometry(object) or close_lines_if_possible) and len(coords) > 2:
                coords = ensure_closed(coords)
                template = "POLYGON((%s))"
            else:
                template = "LINESTRING(%s)"
            coords_text = coords_to_text(coords)
            return template%coords_text
        elif object.type is OSMObjectType.relation:
            geom_type = object.tags.get("type", None)
            if geom_type and geom_type == "multipolygon":
                first_related = next(self.related_objects_of(object))
                multi = None
                if "role" in first_related.tags and first_related.tags["role"] in {"inner", "outer"}:
                    multi = self._construct_multipolygon_from_complex_polygons(object)
                else:
                    multi =  self._construct_multipolygon_from_polygons(object)
                if multi:
                    return multi
                else: # Geometry collection fallback
                    return "GEOMETRYCOLLECTION(%s)"%", ".join(geom for geom in (self.get_geometry_as_wkt(related) for related in self.related_objects_of(object)) if geom)
            else:
                return "GEOMETRYCOLLECTION(%s)"%", ".join(geom for geom in (self.get_geometry_as_wkt(related) for related in self.related_objects_of(object)) if geom)


    def _construct_multipolygon_from_complex_polygons(self, object):
        outers = []
        inners = []
        for related in self.related_objects_of(object):
            if "role" not in related.tags:
                log.warn("Complex multipolygon part %s missing role specifier.", related)
                return None
            if related.type is not OSMObjectType.way:
                log.warn("Creating a point sequence from object of type %s not supported yet.", object.type.name)
                return None
            points = self._get_way_coords(related)
            if related.tags["role"] == "outer":
                outers.append(points)
            elif related.tags["role"] == "inner":
                inners.append(points)
            else:
                log.warn("Unknown multipolygon part role %s.", related.tags["role"])
                return None
        outers = connect_polygon_segments(outers)
        inners = connect_polygon_segments(inners)
        if len(outers) != 1 and len(inners):    
            log.warn("Multiple outer rings and some inner ring(s), ambiguous.")
            return None
        polys = []
        for inner in inners:
            if len(inner) < 4:
                log.warn("Not enough polygon points, falling back to geometry collection for relation %s.", object.id)
                return None
            polys.append("((%s),(%s))"%(coords_to_text(outers[0]), coords_to_text(inner)))
        if not inners:
            for outer in outers:
                if len(outer) < 4:
                    log.warn("Not enough polygon points, falling back to geometry collection for relation %s.", object.id)
                    return None

                polys.append("((%s))"%coords_to_text(outer))
        if len(polys) == 1:
            return "POLYGON%s"%polys[0]
        else:
            return "MULTIPOLYGON(%s)"%", ".join(polys)
    def _construct_multipolygon_from_polygons(self, object):
        parts = []
        for related in self.related_objects_of(object):
            rel_geom = self.get_geometry_as_wkt(related)
            if not rel_geom.startswith("POLYGON"):
                log.warn("Multipolygon promise broken for object %s with geometry %s.", related, rel_geom)
                continue
            parts.append(rel_geom.replace("POLYGON", ""))
            return "MULTIPOLYGON(%s)"%", ".join(parts)
    @property
    def relations(self):
        return self._rels.values()

    @property
    def ways(self):
        return self._ways.values()

    @property
    def nodes(self):
        return self._nodes.values()

    @property
    def cached_relations(self):
        return len(self._rels)

    @property
    def cached_ways(self):
        return len(self._ways)

    @property
    def cached_nodes(self):
        return len(self._nodes)
    
    def lookup_differences_in(self, area, after, timeout=900):
        retrieve_data = self._retrieve_data_template.format(area=area)
        query = self._diff_template.format(after=after, timeout=timeout, query=retrieve_data)
        log.info("Retrieving augmented diff for area %s starting from %s.", area, after)
        xml_data = self._run_query(query, timeout=timeout, is_lookup=False, format="xml")
        root = et.fromstring(xml_data)
        return [OSMObjectChange.from_xml(element) for element in root.findall("action")]
