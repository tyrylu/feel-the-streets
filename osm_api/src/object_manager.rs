use crate::change::OSMObjectChangeEvent;
use crate::change_iterator::OSMObjectChangeIterator;
use crate::object::{OSMObject, OSMObjectSpecifics, OSMObjectType};
use crate::overpass_api::Servers;
use crate::raw_object::OSMObject as RawOSMObject;
use crate::utils;
use crate::{Error, Result};
use chrono::{DateTime, Utc};
use geo_types::{Geometry, GeometryCollection, LineString, Point, Polygon};
use hashbrown::HashMap;
use itertools::Itertools;
use log::{debug, info, trace, warn};
use once_cell::sync::Lazy;
use quick_xml::de::Deserializer;
use serde::Deserialize;
use sled::Db;
use smol_str::SmolStr;
use std::cell::{Ref, RefCell};
use std::cmp;
use std::collections::HashSet;
use std::fs;
use std::io::{BufRead, BufReader, Read};
use std::sync::{Arc, Mutex};
use std::time::Instant;
use zstd_util::ZstdContext;

const COMPRESSION_LEVEL: i32 = 10;

static ZSTD_CONTEXT: Lazy<Mutex<ZstdContext>> = Lazy::new(|| {
    let dict = fs::read("fts.dict").expect("Could not read ZSTD dictionary.");
    Mutex::new(ZstdContext::new(COMPRESSION_LEVEL, Some(&dict)))
});

fn serialize_and_compress(object: &OSMObject) -> Result<Vec<u8>> {
    let serialized = bincode::serialize(&object)?;
    Ok(ZSTD_CONTEXT.lock().unwrap().compress(&serialized)?)
}

pub fn open_cache() -> Result<Db> {
    Ok(sled::open("entities_cache")?)
}

fn deserialize_compressed(compressed: &[u8]) -> Result<OSMObject> {
    let serialized = ZSTD_CONTEXT.lock().unwrap().decompress(compressed)?;
    Ok(bincode::deserialize(&serialized)?)
}

fn translate_type_shortcut(shortcut: char) -> &'static str {
    match shortcut {
        'n' => "node",
        'w' => "way",
        'r' => "relation",
        _ => unreachable!(),
    }
}

fn format_query(timeout: u32, maxsize: usize, query: &str) -> String {
    format!("[timeout:{timeout}][maxsize:{maxsize}];{query};out meta;")
}

fn format_data_retrieval(area: i64) -> String {
    format!(r#"((area({area});node(area);area({area});way(area);area({area});rel(area);>>;);>>;)"#)
}

pub struct OSMObjectManager {
    geometries_cache: RefCell<HashMap<SmolStr, Option<Geometry<f64>>>>,
    api_servers: Arc<Servers>,
    cache: Arc<Db>,
    retrieved_from_network: RefCell<HashSet<SmolStr>>,
    cache_queries: RefCell<u32>,
    cache_hits: RefCell<u32>,
}
impl OSMObjectManager {
    /// Use this constructor only if there's only one OSMObjectManager at a time.
    pub fn new() -> Result<Self> {
        Self::new_multithread(Arc::new(Servers::default()), Arc::new(open_cache()?))
    }

    /// Creates an OsmObjectManager in a scenario where each thread has its own instance and there are at least two of these.
    pub fn new_multithread(servers: Arc<Servers>, cache: Arc<Db>) -> Result<Self> {
        Ok(OSMObjectManager {
            api_servers: servers,
            cache,
            geometries_cache: RefCell::new(HashMap::new()),
            retrieved_from_network: RefCell::new(HashSet::new()),
            cache_queries: RefCell::new(0),
            cache_hits: RefCell::new(0),
        })
    }

    pub fn get_ids_retrieved_from_network(&self) -> Ref<HashSet<SmolStr>> {
        self.retrieved_from_network.borrow()
    }

    pub fn cache_object(&self, object: &OSMObject) {
        let compressed = serialize_and_compress(object).expect("Could not serialize object");
        self.cache
            .insert(object.unique_id().as_bytes(), compressed)
            .expect("Could not cache object.");
    }

    fn has_object(&self, id: &str) -> bool {
        *self.cache_queries.borrow_mut() += 1;
        let exists = self.cache.contains_key(id).expect("Cache query failed.");
        if exists {
            *self.cache_hits.borrow_mut() += 1;
        }
        exists
    }

    fn get_cached_object(&self, id: &str) -> Result<Option<OSMObject>> {
        if let Some(data) = self.cache.get(id)? {
            Ok(Some(deserialize_compressed(data.as_ref())?))
        } else {
            Ok(None)
        }
    }

    fn run_query(&self, query: &str, result_to_tempfile: bool) -> Result<Box<dyn Read + Send>> {
        self.api_servers.run_query(query, result_to_tempfile)
    }

    fn cache_objects_from(
        &self,
        readable: Box<dyn Read>,
        return_objects: bool,
    ) -> Result<Vec<OSMObject>> {
        let start = Instant::now();
        let mut objects = Vec::new();
        let mut cached_readable = BufReader::with_capacity(65536, readable);
        let mut line = String::new();
        // Read past the xml declaration, the initial osm tag, and the note and meta tags.
        // Fortunately, every of these has a line of its own.
        for _ in 0..4 {
            cached_readable.read_line(&mut line)?;
        }
        let mut de = Deserializer::from_reader(cached_readable);
        while let Ok(obj) = RawOSMObject::deserialize(&mut de) {
            let internal_object: OSMObject = obj.try_into()?;
            self.retrieved_from_network
                .borrow_mut()
                .insert(internal_object.unique_id());
            self.cache_object(&internal_object);
            if return_objects {
                objects.push(internal_object);
            }
        }
        debug!("Caching finished after {:?}", start.elapsed());
        self.flush_cache();
        Ok(objects)
    }

    pub fn lookup_objects_in(&self, area: i64) -> Result<()> {
        info!("Looking up all objects in area {}.", area);
        // Area retrieval queries are costly, so tell the server about it upfront.
        let query = format_query(900, 1073741824, &format_data_retrieval(area));
        let readable = self.run_query(&query, false)?;
        self.cache_objects_from(readable, false)?;
        // Ensure that we have the object for the area as well, it sometimes might not be returned by the previous query.
        self.lookup_objects(&mut [crate::area_id_to_osm_id(area)])?;
        Ok(())
    }

    fn lookup_objects<S: AsRef<str>>(&self, ids: &mut [S]) -> Result<()> {
        fn batch_size_for_object_type(object_type: char) -> usize {
            match object_type {
                'n' => 4512,
                'w' => 2024,
                'r' => 560,
                val => {
                    panic!("Unsupported object type {val}.");
                }
            }
        }
        fn memory_cost_per_instance(object_type: char) -> usize {
            1073741824 / batch_size_for_object_type(object_type)
        }
        let mut objects: Vec<OSMObject> = Vec::with_capacity(ids.len());
        ids.sort_unstable_by_key(|oid| oid.as_ref().chars().next());
        for (entity_type, entity_ids) in &ids
            .iter()
            .group_by(|oid| oid.as_ref().chars().next().unwrap())
        {
            for chunk in &entity_ids.chunks(batch_size_for_object_type(entity_type)) {
                let ids_str = chunk.map(|c| &(c.as_ref())[1..]).join(",");
                // Note that this way of counting the actual chunk length is inefficient, so if anyone knows of a better way, i am open ears.
                let query = format_query(
                    900,
                    memory_cost_per_instance(entity_type) * (ids_str.matches(',').count() + 1),
                    &format!("{}(id:{})", translate_type_shortcut(entity_type), ids_str),
                );
                let readable = self.run_query(&query, false)?;
                objects.extend(self.cache_objects_from(readable, true)?);
            }
        }
        self.ensure_has_cached_dependencies_for(&objects)?;
        Ok(())
    }

    fn ensure_has_cached_dependencies_for<O: AsRef<OSMObject>>(&self, objects: &[O]) -> Result<()> {
        use self::OSMObjectSpecifics::*;
        let mut missing = vec![];
        let mut total_examined = 0;
        for object in objects {
            match object.as_ref().specifics {
                Node { .. } => continue, // Nodes have no dependencies
                Way { ref nodes, .. } => {
                    for node in nodes {
                        total_examined += 1;
                        let node_id = format!("n{node}");
                        if !self.has_object(&node_id) {
                            debug!("Node with id {} missing.", node_id);
                            missing.push(node_id);
                        }
                    }
                }
                Relation { ref members, .. } => {
                    for member in members {
                        total_examined += 1;
                        if !self.has_object(&member.unique_reference()) {
                            debug!("Object {} is missing.", member.unique_reference());
                            missing.push(member.unique_reference());
                        }
                    }
                }
            }
        }
        if !missing.is_empty() {
            debug!(
                "Out of {} objects {} was missing.",
                total_examined,
                missing.len()
            );
            self.lookup_objects(&mut missing[..])?;
        }
        Ok(())
    }

    fn related_objects_of<'a>(
        &'a self,
        object: &'a OSMObject,
    ) -> Result<impl Iterator<Item = OSMObject> + 'a> {
        self.ensure_has_cached_dependencies_for(&[object])?;
        Ok(object.related_ids().filter_map(move |(id, maybe_role)| {
            let obj = self.get_cached_object(&id);
            match obj {
                Ok(Some(o)) => Some((o, maybe_role)),
                _ => {
                    warn!("The OSM object {} references non-existent object{}, ignoring that particular reference.", object.unique_id(), id);
                    None
            }
        }
            }).map(move |(mut related, maybe_role)| {
                OSMObjectManager::enrich_tags(object, &mut related);
            if let Some(role) = maybe_role {
                related.tags.insert("role".to_string(), role);
            }
            related
        }))
    }

    pub fn get_object(&self, id: &str) -> Result<Option<OSMObject>> {
        if !self.has_object(id) {
            self.lookup_objects(&mut [id])?;
        }
        self.get_cached_object(id)
    }

    fn enrich_tags(parent: &OSMObject, child: &mut OSMObject) {
        child
            .tags
            .insert("parent_id".to_string(), parent.unique_id().to_string());
    }

    fn get_way_coords(&self, way: &OSMObject) -> Result<LineString<f64>> {
        use self::OSMObjectSpecifics::{Node, Way};
        let node_count = match &way.specifics {
            Way { nodes } => nodes.len(),
            _ => {
                warn!("Requested to get a coord sequence for {}.", way.unique_id());
                return Err(Error::NotAWay);
            }
        };
        let mut coords = Vec::with_capacity(node_count);
        for obj in self.related_objects_of(way)? {
            match obj.specifics {
                Node { lon, lat } => {
                    coords.push((lon, lat));
                }
                _ => unreachable!(),
            }
        }
        Ok(coords.into())
    }

    pub fn get_geometry_as_wkb(&self, object: &OSMObject) -> Result<Option<Vec<u8>>> {
        match self.get_geometry_of(object)? {
            None => Ok(None),
            Some(geom) => Ok(Some(
                wkb::geom_to_wkb(&geom).map_err(|e| Error::WKBWriteError(format!("{e:?}")))?,
            )),
        }
    }

    pub fn get_geometry_of(&self, object: &OSMObject) -> Result<Option<Geometry<f64>>> {
        let exists = self
            .geometries_cache
            .borrow()
            .contains_key(&object.unique_id());
        if exists {
            Ok(self.geometries_cache.borrow()[&object.unique_id()].clone())
        } else {
            let res = self.get_geometry_of_uncached(object)?;
            trace!("Object {} has geometry {:?}", object.unique_id(), res);
            self.geometries_cache
                .borrow_mut()
                .insert(object.unique_id(), res.clone());
            Ok(res)
        }
    }

    fn get_geometry_of_uncached(&self, object: &OSMObject) -> Result<Option<Geometry<f64>>> {
        use self::OSMObjectSpecifics::*;
        match object.specifics {
            Node { lon, lat } => Ok(Some(Point::new(lon, lat).into())),
            Way { .. } => {
                let coords = self.get_way_coords(object)?;
                if coords.0.len() <= 1 {
                    warn!("One or zero nodes for object {}", object.unique_id());
                    return Ok(None);
                }
                if utils::object_should_have_closed_geometry(object) && coords.0.len() > 2 {
                    Ok(Some(Polygon::new(coords, vec![]).into()))
                } else {
                    Ok(Some(coords.into()))
                }
            }
            Relation { .. } => {
                let should_be_multipolygon =
                    object.tags.get("type").map(|t| t.as_str()).unwrap_or("") == "multipolygon";
                let mut inners = vec![];
                let mut outers = vec![];
                let mut others = vec![];
                for related in self.related_objects_of(object)? {
                    let role = related.tags.get("role").map(|r| r.as_str()).unwrap_or("");
                    match role {
                        "inner" => self.extend_list_of_polygon_parts(&mut inners, related)?,
                        "outer" => self.extend_list_of_polygon_parts(&mut outers, related)?,
                        _ => others.push(related),
                    }
                }
                inners.dedup();
                outers.dedup();
                let mut multipolygon = None;
                if should_be_multipolygon {
                    if (!outers.is_empty() || !inners.is_empty()) && !others.is_empty() {
                        warn!("Could not create multipolygon from object {}, it has {} inner ring(s), {} outer ring(s) and {} other part(s).", object.unique_id(), inners.len(), outers.len(), others.len());
                    } else if outers.is_empty() {
                        // Likely a multipolygon from a list of outer ring specifications without an explicit role.
                        multipolygon = self.construct_multipolygon_from_parts(
                            object.unique_id(),
                            inners.as_slice(),
                            others.as_slice(),
                        )?;
                    } else {
                        multipolygon = self.construct_multipolygon_from_parts(
                            object.unique_id(),
                            inners.as_slice(),
                            outers.as_slice(),
                        )?;
                    }
                }
                if multipolygon.is_some() {
                    Ok(multipolygon)
                } else if !outers.is_empty() && !should_be_multipolygon {
                    // Try to create a multipolygon from whatewer we have roles for and add it to the rest, if there's any rest.
                    match self.construct_multipolygon_from_parts(
                        object.unique_id(),
                        inners.as_slice(),
                        outers.as_slice(),
                    )? {
                        Some(poly) if others.is_empty() => Ok(Some(poly)),
                        Some(poly) => {
                            let mut coll = GeometryCollection::default();
                            coll.0.push(poly);
                            for o in others {
                                coll.0.append(&mut utils::expand_geometry_collections(&[self.get_geometry_of(&o)?.unwrap()]));
                            }
                            Ok(Some(Geometry::GeometryCollection(coll)))
                        }
                        None => self.create_geometry_collection(object),
                    }
                } else {
                    self.create_geometry_collection(object)
                }
            }
        }
    }

    fn extend_list_of_polygon_parts(
        &self,
        parts: &mut Vec<OSMObject>,
        new_object: OSMObject,
    ) -> Result<()> {
        match new_object.object_type() {
            OSMObjectType::Node => {
                warn!(
                    "A node {} can not be a direct part of a polygon defining relationship.",
                    new_object.unique_id()
                );
            }
            OSMObjectType::Way => {
                parts.push(new_object);
            }
            OSMObjectType::Relation => {
                parts.extend(self.related_objects_of(&new_object)?.filter(|o| o.object_type() == OSMObjectType::Way));
            }
        }
        Ok(())
    }

    fn create_geometry_collection(&self, object: &OSMObject) -> Result<Option<Geometry<f64>>> {
        let mut coll = GeometryCollection::default();
        for related in self.related_objects_of(object)? {
            let related_geom = self.get_geometry_of(&related)?;
            if let Some(related_geom) = related_geom {
            if let Geometry::GeometryCollection(related_coll) = related_geom {
                coll.0.append(&mut utils::expand_geometry_collections(&related_coll.0));
            }
            else {
                coll.0.push(related_geom);
            }
        }
    }
        if coll.len() == 1 {
            Ok(Some(coll.0.pop().unwrap()))
        } else {
            Ok(Some(Geometry::GeometryCollection(coll)))
        }
    }

    fn construct_multipolygon_from_parts(
        &self,
        object_id: SmolStr,
        inner_objects: &[OSMObject],
        outer_objects: &[OSMObject],
    ) -> Result<Option<Geometry<f64>>> {
        let mut inners = vec![];
        let mut outers = vec![];
        for i in inner_objects {
            inners.push(self.get_way_coords(i)?);
        }
        for o in outer_objects {
            outers.push(self.get_way_coords(o)?);
        }
        utils::connect_polygon_segments(&mut inners);
        utils::connect_polygon_segments(&mut outers);
        if outers.len() != 1 && !inners.is_empty() {
            warn!("multiple outer ring(s) and some inner ring(s), geometry for object {object_id} is ambiguous.");
            return Ok(None);
        }
        let mut polys = Vec::with_capacity(cmp::max(inners.len(), outers.len()));
        if inners.is_empty() {
            // A possible multipolygon given a list of outer rings.
            // The number of needed points, e. g. 4 or more, is because the polygon closing logic closes the polygon, which adds a point, so we need at-least 3 original ones.
            for outer in outers {
                if outer.0.len() < 4 {
                    warn!("One of the outer rings of object {object_id} did not have enough points, falling back to a geometry collection.");
                    return Ok(None);
                }
                polys.push(Polygon::new(outer, vec![]));
            }
        } else {
            // A single polygon given an outer ring and list of inner hole rings.
            // The magic number of points has the same reason as above.
            for inner in &inners {
                if inner.0.len() < 4 {
                    warn!("One of the inner polygons for object {object_id} did not have enough points, falling back to a geometry collection.");
                    return Ok(None);
                }
            }
            polys.push(Polygon::new(outers[0].clone(), inners.clone()))
        }
        if polys.len() == 1 {
            Ok(Some(polys[0].clone().into()))
        } else {
            Ok(Some(Geometry::MultiPolygon(polys.into())))
        }
    }

    fn flush_cache(&self) {
        self.cache.flush().expect("Flush failed.");
    }

    pub fn lookup_differences_in(
        &self,
        area: i64,
        after: &DateTime<Utc>,
    ) -> Result<Box<dyn Iterator<Item = Result<OSMObjectChangeEvent>>>> {
        let mut iterators = Vec::with_capacity(3);
        for kind in &["node", "way", "rel"] {
            let query = format!("((area({area});{kind}(area);>>;);>>;)");
            let final_query = format!(
                "[out:xml][timeout:900][adiff:\"{after}\"];{query};out meta;",
                after = after.to_rfc3339(),
                query = query
            );
            info!("Looking up differences in area {}, {}s only.", area, kind);
            let readable = self.run_query(&final_query, true)?;
            iterators.push(OSMObjectChangeIterator::new(readable));
        }
        Ok(Box::new(iterators.into_iter().flatten()))
    }

    pub fn get_area_parents(&self, area_id: i64) -> Result<Vec<OSMObject>> {
        let query = format!("rel({});<<;out meta;", area_id - 3_600_000_000);
        let readable = self.run_query(&query, false)?;
        self.cache_objects_from(readable, true)
    }

    pub fn cached_objects(&self) -> Box<dyn (Iterator<Item = OSMObject>)> {
        Box::new(
            self.cache
                .iter()
                .filter_map(|pair| pair.ok())
                .map(|(_k, v)| deserialize_compressed(&v).expect("Could not deserialize object")),
        )
    }

    pub fn remove_cached_object(&self, id: &str) -> Result<()> {
        self.cache.remove(id)?;
        Ok(())
    }
}

impl Drop for OSMObjectManager {
    fn drop(&mut self) {
        info!(
            "Out of {} entity cache queries {} were cache hits.",
            self.cache_queries.borrow(),
            self.cache_hits.borrow()
        );
    }
}
