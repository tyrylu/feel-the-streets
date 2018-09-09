use itertools::Itertools;
use osm::error::Result;
use osm::object::{OSMObject, OSMObjectSpecifics};
use reqwest::{self, StatusCode};
use rusqlite::Connection;
use serde::Deserialize;
use serde_json::{self, Deserializer};
use sqlitemap::SqliteMap;
use std::collections::HashMap;
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
    current_api_url_idx: usize,
    api_urls: Vec<&'static str>,
    cache_conn: Connection,
    http_client: reqwest::Client
}

impl OSMObjectManager {
    pub fn new() -> Self {
        let client = reqwest::Client::builder().timeout(None).build().expect("Failed to create http client.");
        OSMObjectManager {
            api_urls: vec![
                "https://z.overpass-api.de/api",
                "https://lz4.overpass-api.de/api",
            ],
            current_api_url_idx: 0 as usize,
            cache_conn: Connection::open("entity_cache.db").unwrap(),
            http_client: client
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
            )
            .expect("Could not cache object.");
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

    fn next_api_url(&mut self) -> &'static str {
        if self.current_api_url_idx == self.api_urls.len() {
            self.current_api_url_idx = 0 as usize;
        }
        self.api_urls[self.current_api_url_idx]
    }

    fn run_query(&mut self, query: &str) -> Result<Box<Read>> {
        let url = self.next_api_url();
        let final_url = format!("{}/interpreter?data={}", url, query);
        let resp = self.http_client.get(&final_url).send()?;
        match resp.status() {
            StatusCode::TooManyRequests => {
                warn!("Multiple requests, killing them and going to a different api host.");
                self.http_client.get(&format!("{0}/kill_my_queries", &url)).send()?;
                return self.run_query(&query);
            }
            StatusCode::Ok => {
                return Ok(Box::new(resp));
            }
            _ => {
                warn!("Unexpected status code {} from the server.", resp.status());
                return self.run_query(&query);
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

    pub fn lookup_objects_in(&mut self, area: &str) -> Result<()> {
        let query = format_query(900, &format_data_retrieval(area));
        let readable = self.run_query(&query)?;
        self.cache_objects_from(readable, false)?;
        Ok(())
    }

    fn lookup_objects(&mut self, ids: &mut [String]) -> Result<()> {
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

    fn ensure_has_cached_dependencies_for(&mut self, objects: &[OSMObject]) -> Result<()> {
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

    fn related_ids_of(&mut self, object: &OSMObject) -> Result<Box<Iterator<Item = String>>> {
        use self::OSMObjectSpecifics::*;
        match object.specifics {
            Node { .. } => Ok(Box::new(iter::empty())),
            Way { ref nodes, .. } => {
                self.ensure_has_cached_dependencies_for(&[object.clone()])?;
                Ok(Box::new(
                    nodes.clone().into_iter().map(|n| format!("n{}", n)),
                ))
            }
            Relation { ref members, .. } => {
                self.ensure_has_cached_dependencies_for(&[object.clone()])?;
                Ok(Box::new(
                    members.clone().into_iter().map(|m| m.unique_reference()),
                ))
            }
        }
    }

    fn related_objects_of<'a>(&'a mut self, object: &OSMObject) -> Result<impl Iterator + 'a> {
        Ok(self
            .related_ids_of(&object)?
            .map(move |i| self.get_cached_object(&i).unwrap()))
    }

    pub fn get_object(&mut self, id: &str) -> Result<Option<OSMObject>> {
        if !self.has_object(&id) {
            self.lookup_objects(&mut [id.to_string()])?;
        }
        Ok(self.get_cached_object(&id))
    }
    fn enrich_tags(parent: &OSMObject, child: &mut OSMObject) {
        child.tags.insert("parent_id".to_string(), parent.unique_id());
    }
}
