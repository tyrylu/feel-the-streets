use std::{collections::HashMap, path::Path, fs::File};
use osm_api::{object::OSMObject, SmolStr};
use crate::Result;

pub(crate) type CacheMap = HashMap<SmolStr, HashMap<String, String>>;

pub struct OSMObjectNamesCache {
    cache: CacheMap
}

impl OSMObjectNamesCache {
    
    pub fn load() -> Result<Self> {
        Self::load_from("osm_object.names")
    }

    fn load_from(path: &str) -> Result<Self> {
        let dest = Path::new(path);
        let cache: CacheMap = if dest.exists() {
            serde_json::from_reader(File::open(dest)?)?
        }
        else {
            CacheMap::new()
        };
        Ok(Self{cache})
    }

    pub fn cache_names_of(&mut self, object: &OSMObject) {
        let names = self.cache.entry(object.unique_id()).or_default();
        for (key, value) in &object.tags {
            if key.starts_with("name") {
                let language = if key.contains(':') {
                    key.split(':').nth(1).unwrap()
                } else {
                    "native"
                };
                names.insert(language.to_string(), value.to_string());
            }
        }
    }

    pub fn save(&self) -> Result<()> {
        let dest = File::create("osm_object.names")?;
        serde_json::to_writer(dest, &self.cache)?;
        Ok(())
    }

    pub fn into_cache_map(self) -> CacheMap {
        self.cache
    }
}