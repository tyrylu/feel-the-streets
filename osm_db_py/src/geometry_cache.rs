use crate::geometry::{parse_wkb, PyGeometry};
use dashmap::DashMap;
use geo::Geometry;
use once_cell::sync::Lazy;
use std::sync::Arc;

/// Global cache: maps entity OSM id → parsed geometry.
/// Entities are immutable after creation, so this cache never needs invalidation.
static GEOMETRY_CACHE: Lazy<DashMap<String, Arc<Geometry<f64>>>> = Lazy::new(DashMap::new);

/// Return the cached geometry for the given entity id, parsing the WKB bytes if not yet cached.
pub fn get_or_parse(entity_id: &str, wkb_bytes: &[u8]) -> PyGeometry {
    if let Some(cached) = GEOMETRY_CACHE.get(entity_id) {
        return PyGeometry::new(cached.clone());
    }
    let geom = Arc::new(parse_wkb(wkb_bytes));
    GEOMETRY_CACHE.insert(entity_id.to_string(), geom.clone());
    PyGeometry::new(geom)
}
