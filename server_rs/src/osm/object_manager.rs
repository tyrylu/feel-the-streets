use itertools::Itertools;
use osm::error::Result;
use osm::object::{OSMObject, OSMObjectSpecifics, OSMObjectType};
use osm::utils;
use reqwest::{self, StatusCode};
use rusqlite::Connection;
use serde::Deserialize;
use serde_json::{self, Deserializer};
use sqlitemap::SqliteMap;
use std::cell::RefCell;
use std::io::{BufReader, Read};
use std::iter;

fn translate_type_shortcut(shortcut: &char) -> &'static str {
    match shortcut {
        'n' => "node",
        'w' => "way",
        'r' => "relation",
        _ => unreachable!(),
    }
}

fn format_query(timeout: u32, query: &str) -> String {
    format!(
        "[out:json][timeout:{timeout}];{query};out meta;",
        timeout = timeout,
        query = query
    )
}

fn format_data_retrieval(area: &str) -> String {
    format!(r#"((area["name"="{area}"];node(area);area["name"="{area}"];way(area);area["name"="{area}"];rel(area);>>;);>>;)"#, area = area)
}

pub struct OSMObjectManager {
    current_api_url_idx: RefCell<usize>,
    api_urls: Vec<&'static str>,
    cache_conn: Connection,
    http_client: reqwest::Client,
}

impl OSMObjectManager {
    pub fn new() -> Self {
        let client = reqwest::Client::builder()
            .timeout(None)
            .build()
            .expect("Failed to create http client.");
        OSMObjectManager {
            api_urls: vec![
                "https://z.overpass-api.de/api",
                "https://lz4.overpass-api.de/api",
            ],
            current_api_url_idx: RefCell::new(0 as usize),
            cache_conn: Connection::open("entity_cache.db").unwrap(),
            http_client: client,
        }
    }

    fn get_cache(&self) -> SqliteMap {
        SqliteMap::new(&self.cache_conn, "raw_entities", "text", "text").unwrap()
    }

    fn cache_object(&self, object: &OSMObject) {
        let mut cache = self.get_cache();
        cache
            .insert::<String>(
                &object.unique_id(),
                &serde_json::to_string(&object).expect("Could not serialize object for caching."),
            ).expect("Could not cache object.");
    }

    fn has_object(&self, id: &str) -> bool {
        let mut cache = self.get_cache();
        cache.contains_key(&id).expect("Cache query failed.")
    }

    fn get_cached_object(&self, id: &str) -> Option<OSMObject> {
        let mut cache = self.get_cache();
        cache
            .get::<String>(&id)
            .expect("Cache retrieval failed.")
            .map(|o| serde_json::from_str(&o).expect("Failed to deserialize cached object."))
    }

    fn next_api_url(&self) -> &'static str {
        if *self.current_api_url_idx.borrow() == self.api_urls.len() {
            *self.current_api_url_idx.borrow_mut() = 0 as usize;
        }
        self.api_urls[*self.current_api_url_idx.borrow()]
    }

    fn run_query(&self, query: &str) -> Result<Box<Read>> {
        let url = self.next_api_url();
        let final_url = format!("{}/interpreter?data={}", url, query);
        let resp = self.http_client.get(&final_url).send()?;
        match resp.status() {
            StatusCode::TooManyRequests => {
                warn!("Multiple requests, killing them and going to a different api host.");
                self.http_client
                    .get(&format!("{0}/kill_my_queries", &url))
                    .send()?;
                self.run_query(&query)
            }
            StatusCode::Ok => Ok(Box::new(resp)),
            _ => {
                warn!("Unexpected status code {} from the server.", resp.status());
                self.run_query(&query)
            }
        }
    }

    fn cache_objects_from(
        &self,
        readable: Box<Read>,
        return_objects: bool,
    ) -> Result<Vec<OSMObject>> {
        let mut objects = Vec::new();
        let mut cached_readable = BufReader::with_capacity(65536, readable);
        let mut buf = [0; 1];
        loop {
            let _bytes = cached_readable.read(&mut buf)?;
            if String::from_utf8_lossy(&buf[..]) == "[" {
                break;
            }
        }
        // We're past the data header, only objects follow.
        loop {
            {
                let mut de = Deserializer::from_reader(&mut cached_readable);
                match OSMObject::deserialize(&mut de) {
                    Ok(obj) => {
                        self.cache_object(&obj);
                        if return_objects {
                            objects.push(obj);
                        }
                    }
                    Err(_e) => break,
                }
            }
            cached_readable.read(&mut buf)?; // Skip a comma
        }
        Ok(objects)
    }

    pub fn lookup_objects_in(&self, area: &str) -> Result<()> {
        let query = format_query(900, &format_data_retrieval(area));
        let readable = self.run_query(&query)?;
        self.cache_objects_from(readable, false)?;
        Ok(())
    }

    fn lookup_objects(&self, ids: &mut [String]) -> Result<()> {
        const MAX_SIMULTANEOUSLY_QUERYED: usize = 1000000;
        let mut objects: Vec<OSMObject> = vec![];
        ids.sort_unstable_by_key(|oid| oid.chars().nth(0));
        for (entity_type, entity_ids) in
            &ids.into_iter().group_by(|oid| oid.chars().nth(0).unwrap())
        {
            for mut chunk in entity_ids.chunks(MAX_SIMULTANEOUSLY_QUERYED).into_iter() {
                let ids_str = chunk.join(",");
                let query = format_query(
                    900,
                    &format!("{}(id:{})", translate_type_shortcut(&entity_type), ids_str),
                );
                let readable = self.run_query(&query)?;
                objects.extend(self.cache_objects_from(readable, true)?);
            }
        }
        self.ensure_has_cached_dependencies_for(&objects)?;
        Ok(())
    }

    fn ensure_has_cached_dependencies_for(&self, objects: &[OSMObject]) -> Result<()> {
        use self::OSMObjectSpecifics::*;
        let mut missing = vec![];
        for object in objects {
            match object.specifics {
                Node { .. } => continue, // Nodes have no dependencies
                Way { ref nodes, .. } => {
                    for node in nodes {
                        let node_id = format!("n{}", node);
                        if !self.has_object(&node_id) {
                            debug!("Node with id {} missing.", node_id);
                            missing.push(node_id);
                        }
                    }
                }
                Relation { ref members, .. } => {
                    for member in members {
                        if !self.has_object(&member.unique_reference()) {
                            debug!("Object {} is missing.", member.unique_reference());
                            missing.push(member.unique_reference());
                        }
                    }
                }
            }
        }
        if missing.len() > 0 {
            info!(
                "Out of {} objects {} was missing.",
                objects.len(),
                missing.len()
            );
            self.lookup_objects(&mut missing[..])?;
        }
        Ok(())
    }

    fn related_ids_of<'a>(
        &'a self,
        object: &'a OSMObject,
    ) -> Result<Box<Iterator<Item = (String, Option<String>)>>> {
        use self::OSMObjectSpecifics::*;
        match object.specifics {
            Node { .. } => Ok(Box::new(iter::empty())),
            Way { ref nodes, .. } => {
                self.ensure_has_cached_dependencies_for(&[object.clone()])?;
                Ok(Box::new(
                    nodes.clone().into_iter().map(|n| (format!("n{}", n), None)),
                ))
            }
            Relation { ref members, .. } => {
                self.ensure_has_cached_dependencies_for(&[object.clone()])?;
                Ok(Box::new(
                    members
                        .clone()
                        .into_iter()
                        .map(|m| (m.unique_reference(), Some(m.role))),
                ))
            }
        }
    }
    fn related_objects_of<'a>(
        &'a self,
        object: &'a OSMObject,
    ) -> Result<impl Iterator<Item = OSMObject> + 'a> {
        Ok(self.related_ids_of(&object)?.map(move |(id, maybe_role)| {
            let mut related = self.get_cached_object(&id).unwrap();
            OSMObjectManager::enrich_tags(&object, &mut related);
            if let Some(role) = maybe_role {
                related.tags.insert("role".to_string(), role);
            }
            related
        }))
    }

    pub fn get_object(&self, id: &str) -> Result<Option<OSMObject>> {
        if !self.has_object(&id) {
            self.lookup_objects(&mut [id.to_string()])?;
        }
        Ok(self.get_cached_object(&id))
    }

    fn enrich_tags(parent: &OSMObject, child: &mut OSMObject) {
        child
            .tags
            .insert("parent_id".to_string(), parent.unique_id());
    }

    fn get_way_coords(&self, way: &OSMObject) -> Result<Vec<(f64, f64)>> {
        use self::OSMObjectSpecifics::Node;
        let mut coords = vec![];
        for obj in self.related_objects_of(&way)? {
            match obj.specifics {
                Node { lon, lat } => {
                    coords.push((lon, lat));
                }
                _ => unreachable!(),
            }
        }
        Ok(coords)
    }

    pub fn get_geometry_as_wkt(&self, object: &OSMObject) -> Result<Option<String>> {
        use self::OSMObjectSpecifics::*;
        match object.specifics {
            Node { lon, lat } => Ok(Some(format!("POINT({},{})", lon, lat))),
            Way { ref nodes } => {
                let mut coords = self.get_way_coords(&object)?;
                if coords.len() <= 1 {
                    warn!("One or zero nodes for object {}", object.unique_id());
                    return Ok(None);
                }
                let coords_text = utils::coords_to_text(&coords);
                if utils::object_should_have_closed_geometry(&object) && coords.len() > 2 {
                    utils::ensure_closed(&mut coords);
                    Ok(Some(format!("POLYGON(({}))", coords_text)))
                } else {
                    Ok(Some(format!("LINESTRING({})", coords_text)))
                }
            }
            Relation { ref members } => {
                let empty = "".to_string();
                let geom_type = object
                    .tags
                    .get(&"type".to_string()).unwrap_or(&empty);
                if geom_type == &"multipolygon".to_string() {
                    let first_related = self.related_objects_of(&object)?.next().unwrap();
                    let mut multi = None;
                    match first_related.tags.get("role").unwrap_or(&"".to_string()).as_ref() {
                        "inner" | "outer" => {
                            multi = self.construct_multipolygon_from_complex_polygons(&object)?;
                        }
                        _ => {
                            multi = self.construct_multipolygon_from_polygons(&object)?;
                        }
                    }
                    if let Some(geom) = multi {
                        Ok(Some(geom))
                    } else {
                        self.create_geometry_collection(&object)
                    }
                } else {
                    self.create_geometry_collection(&object)
                }
            }
        }
    }
    
    fn create_geometry_collection(&self, object: &OSMObject) -> Result<Option<String>> {
        Ok(Some(format!(
            "GEOMETRYCOLLECTION({})",
            self.related_objects_of(&object)?
                .map(|o| self.get_geometry_as_wkt(&o))
                .filter_map(|g| g.ok())
                .filter_map(|g| g)
                .join(", ")
        )))
    }
    
    fn construct_multipolygon_from_polygons(&self, object: &OSMObject) -> Result<Option<String>> {
        let mut parts = vec![];
        for related in self.related_objects_of(&object)? {
            let rel_geom = self.get_geometry_as_wkt(&related)?.unwrap();
            if !rel_geom.starts_with("POLYGON") {
                warn!("Multipolygon promise broken for object with id {}", related.unique_id());
                return Ok(None);
            }
            parts.push(rel_geom.replace("POLYGON", ""));
        }
        Ok(Some(format!("MULTIPOLYGON({})", parts.join(", "))))
    }

    fn construct_multipolygon_from_complex_polygons(&self, object: &OSMObject) -> Result<Option<String>> {
        let mut inners = vec![];
        let mut outers = vec![];
        for related in self.related_objects_of(&object)? {
            if !related.tags.contains_key(&"role".to_string()) {
                warn!("Missing role specifier for object {} as part of geometry of object {}", related.unique_id(), object.unique_id());
                return Ok(None);
            }
            if !(related.object_type() == OSMObjectType::Way) {
                warn!("Creation of a point sequence for object {} not supported/impossible.", related.unique_id());
                return Ok(None);
            }
            let points = self.get_way_coords(&related);
            match related.tags["role"].as_ref() {
                "inner" => inners.push(points),
                "outer" => outers.push(points),
                _ => {
                    warn!("Unknown multipolygon part tole {}.", related.tags["role"]);
                    return Ok(None);
                }
            }
        }
        Ok(None)
    }
}
