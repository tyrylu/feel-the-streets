use osm_api::BoundaryRect;
use osm_api::object::{OSMObject, OSMObjectType};
use osm_api::object_manager::OSMObjectManager;
use crate::Result;
use rusqlite::named_params;
pub use rusqlite::Connection;

pub fn connect_to_server_db() -> Result<Connection> {
    let conn = Connection::open("server.db")?;
    unsafe {
        conn.load_extension_enable()?;
        conn.load_extension("mod_spatialite", None)?;
    }
    conn.load_extension_disable()?;
    conn.execute("CREATE TABLE IF NOT EXISTS area_entities (area_id INTEGER, entity_id TEXT, PRIMARY KEY (area_id, entity_id))", [])?;
    conn.execute("CREATE TABLE IF NOT EXISTS entity_geometry_parts (entity_id TEXT, contained_entity_id TEXT, PRIMARY KEY (entity_id, contained_entity_id))", [])?;
    conn.execute("CREATE INDEX IF NOT EXISTS idx_area_entities_by_entity_id ON area_entities(entity_id)", [])?;
    conn.execute("CREATE INDEX IF NOT EXISTS idx_entity_geometry_parts_by_contained_entity_id ON entity_geometry_parts(contained_entity_id)", [])?;
    Ok(conn)
}

pub fn get_geometry_bounds(conn: &Connection, geometry: &[u8]) -> Result<BoundaryRect> {
    trace!("Getting bounds of geometry {:?}", geometry);
    let mut stmt = conn.prepare_cached("SELECT MbrMinX(GeomFromWkb(:geom, 4326)) as minx, MbrMinY(GeomFromWkb(:geom, 4326)) as miny, MbrMaxX(GeomFromWkb(:geom, 4326)) as maxx, MbrMaxY(GeomFromWkb(:geom, 4326)) as maxy")?;
    Ok(stmt.query_row(named_params! {":geom": geometry}, |r| Ok(BoundaryRect {
        min_x: r.get_unwrap(0),
        min_y: r.get_unwrap(1),
        max_x: r.get_unwrap(2),
        max_y: r.get_unwrap(3)
    }))?)
}

pub fn insert_area_entity(conn: &Connection, area_id: i64, entity_id: &str) -> Result<()> {
    let mut stmt = conn.prepare_cached("INSERT OR REPLACE INTO area_entities (area_id, entity_id) VALUES (?, ?)")?;
    stmt.execute((area_id, entity_id))?;
    Ok(())
}

pub fn insert_entity_geometry_parts(conn: &Connection, manager: &OSMObjectManager, object: &OSMObject) -> Result<()> {
    begin_transaction(conn)?;
    insert_entity_geometry_parts_of(object.unique_id().as_str(), object, conn, manager)?;
    commit_transaction(conn)
}

fn insert_entity_geometry_parts_of(entity_id: &str, object: &OSMObject, conn: &Connection, manager: &OSMObjectManager) -> Result<()> {
    match object.object_type() {
        OSMObjectType::Node => {},
        OSMObjectType::Way => {
            for (nid, _) in object.related_ids() {
                insert_entity_geometry_part(conn, entity_id, &nid)?;
            }
        },
        OSMObjectType::Relation => {
            for (oid, _) in object.related_ids() {
                insert_entity_geometry_part(conn, entity_id, &oid)?;
                if let Some(related_object) = manager.get_object(&oid)? {
                    insert_entity_geometry_parts_of(entity_id, &related_object, conn, manager)?;
                }
            }
        }
    }
    Ok(())
}

fn insert_entity_geometry_part(conn: &Connection, entity_id: &str, contained_entity_id: &str) -> Result<()> {
    let mut stmt = conn.prepare_cached("INSERT OR REPLACE INTO entity_geometry_parts (entity_id, contained_entity_id) VALUES (?, ?)")?;
    stmt.execute((entity_id, contained_entity_id))?;
    Ok(())
}

fn begin_transaction(conn: &Connection) -> Result<()> {
    conn.execute("BEGIN", [])?;
    Ok(())
}

fn commit_transaction(conn: &Connection) -> Result<()> {
    conn.execute("COMMIT", [])?;
    Ok(())
}

pub fn newest_osm_object_timestamp(conn: &Connection) -> Result<String> {
    let mut stmt = conn.prepare_cached("SELECT max(newest_osm_object_timestamp) from areas")?;
    Ok(stmt.query_row([], |r| Ok(r.get_unwrap(0)))?)
}

pub fn areas_containing(entity_id: &str, conn: &Connection) -> Result<Vec<i64>> {
    let mut stmt = conn.prepare_cached("SELECT area_id from area_entities WHERE entity_id = ?")?;
    let ids = stmt.query_map([entity_id], |r| Ok(r.get_unwrap(0)))?.map(|a| a.expect("Could not get area id")).collect();
    Ok(ids)
}

pub fn entities_containing(child_id: &str, conn: &Connection) -> Result<Vec<String>> {
    let mut stmt = conn.prepare_cached("SELECT entity_id from entity_geometry_parts WHERE contained_entity_id = ?")?;
    let ids = stmt.query_map([child_id], |r| Ok(r.get_unwrap(0)))?.map(|a| a.expect("Could not get area id")).collect();
    Ok(ids)
}

pub(crate) fn delete_entity_records(conn: &Connection, entity_id: &str) -> Result<()> {
    delete_entity_geometry_parts(conn, entity_id)?;
    let mut del_entity_stmt = conn.prepare_cached("DELETE FROM area_entities WHERE entity_id = ?")?;
    del_entity_stmt.execute([entity_id])?;
    Ok(())
}

pub(crate) fn delete_entity_geometry_parts(conn: &Connection, entity_id: &str) -> Result<()> {
    let mut del_geometry_parts_stmt = conn.prepare_cached("DELETE FROM entity_geometry_parts WHERE entity_id = ?")?;
    del_geometry_parts_stmt.execute([entity_id])?;
   Ok(())
}

pub(crate) fn delete_area_entity(conn: &Connection, area_id: i64, entity_id: &str) -> Result<()> {
    let mut del_entity_stmt = conn.prepare_cached("DELETE FROM area_entities WHERE area_id = ? AND entity_id = ?")?;
    del_entity_stmt.execute((area_id, entity_id))?;
    Ok(())
}