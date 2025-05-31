mod changeset;

use self::changeset::Changeset;
pub use self::changeset::InsertableChangeset;
use crate::Result;
use osm_api::object::{OSMObject, OSMObjectType};
use osm_api::object_manager::OSMObjectManager;
use osm_api::{BoundaryRect, SmolStr};
use rusqlite::{named_params, LoadExtensionGuard};
pub use rusqlite::Connection;
use std::collections::HashSet;

pub fn connect_to_server_db() -> Result<Connection> {
    let conn = Connection::open("server.db")?;
    unsafe {
        let _guard = LoadExtensionGuard::new(&conn)?;
        conn.load_extension("mod_spatialite", None::<&str>)?;
    }
    conn.execute("CREATE TABLE IF NOT EXISTS area_entities (area_id INTEGER, entity_id TEXT, PRIMARY KEY (area_id, entity_id))", [])?;
    conn.execute("CREATE TABLE IF NOT EXISTS entity_geometry_parts (entity_id TEXT, contained_entity_id TEXT, PRIMARY KEY (entity_id, contained_entity_id))", [])?;
    conn.execute("CREATE TABLE IF NOT EXISTS changesets (changeset_id INTEGER primary key, changesets_batch INTEGER, min_lat FLOAT, max_lat FLOAT, min_lon FLOAT, max_lon FLOAT)", [])?;
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_area_entities_by_entity_id ON area_entities(entity_id)",
        [],
    )?;
    conn.execute("CREATE INDEX IF NOT EXISTS idx_entity_geometry_parts_by_contained_entity_id ON entity_geometry_parts(contained_entity_id)", [])?;
    Ok(conn)
}

pub fn get_geometry_bounds(conn: &Connection, geometry: &[u8]) -> Result<BoundaryRect> {
    trace!("Getting bounds of geometry {:?}", geometry);
    let mut stmt = conn.prepare_cached("SELECT MbrMinX(GeomFromWkb(:geom, 4326)) as minx, MbrMinY(GeomFromWkb(:geom, 4326)) as miny, MbrMaxX(GeomFromWkb(:geom, 4326)) as maxx, MbrMaxY(GeomFromWkb(:geom, 4326)) as maxy")?;
    Ok(stmt.query_row(named_params! {":geom": geometry}, |r| {
        Ok(BoundaryRect {
            min_x: r.get_unwrap(0),
            min_y: r.get_unwrap(1),
            max_x: r.get_unwrap(2),
            max_y: r.get_unwrap(3),
        })
    })?)
}

pub fn insert_area_entity(conn: &Connection, area_id: i64, entity_id: &str) -> Result<()> {
    let mut stmt = conn.prepare_cached(
        "INSERT OR REPLACE INTO area_entities (area_id, entity_id) VALUES (?, ?)",
    )?;
    stmt.execute((area_id, entity_id))?;
    Ok(())
}

pub fn insert_entity_geometry_parts(
    conn: &Connection,
    manager: &OSMObjectManager,
    object: &OSMObject,
) -> Result<()> {
    let savepoint_name = format!("insert_entities_for_{}", object.unique_id());
    begin_savepoint(conn, &savepoint_name)?;
    let mut seen_ids = HashSet::from([object.unique_id()]);
    insert_entity_geometry_parts_of(
        object.unique_id().as_str(),
        object,
        conn,
        manager,
        &mut seen_ids,
    )?;
    commit_savepoint(conn, &savepoint_name)
}

fn insert_entity_geometry_parts_of(
    entity_id: &str,
    object: &OSMObject,
    conn: &Connection,
    manager: &OSMObjectManager,
    seen_ids: &mut HashSet<SmolStr>,
) -> Result<()> {
    match object.object_type() {
        OSMObjectType::Node => {}
        OSMObjectType::Way => {
            for (nid, _) in object.related_ids() {
                insert_entity_geometry_part(conn, entity_id, &nid)?;
            }
        }
        OSMObjectType::Relation => {
            for (oid, _) in object.related_ids() {
                if seen_ids.contains(&oid) {
                    debug!("When inserting the geometry parts of {}, we already inserted {}, skipping.", entity_id, oid);
                    continue;
                } else {
                    seen_ids.insert(oid.clone());
                    insert_entity_geometry_part(conn, entity_id, &oid)?;
                    if let Some(related_object) = manager.get_object(&oid)? {
                        insert_entity_geometry_parts_of(
                            entity_id,
                            &related_object,
                            conn,
                            manager,
                            seen_ids,
                        )?;
                    }
                }
            }
        }
    }
    Ok(())
}

fn insert_entity_geometry_part(
    conn: &Connection,
    entity_id: &str,
    contained_entity_id: &str,
) -> Result<()> {
    let mut stmt = conn.prepare_cached("INSERT OR REPLACE INTO entity_geometry_parts (entity_id, contained_entity_id) VALUES (?, ?)")?;
    stmt.execute((entity_id, contained_entity_id))?;
    Ok(())
}

pub(crate) fn begin_transaction(conn: &Connection) -> Result<()> {
    conn.execute("BEGIN", [])?;
    Ok(())
}

pub(crate) fn commit_transaction(conn: &Connection) -> Result<()> {
    conn.execute("COMMIT", [])?;
    Ok(())
}

fn begin_savepoint(conn: &Connection, name: &str) -> Result<()> {
    let stmt = format!("SAVEPOINT {}", name);
    conn.execute(&stmt, [])?;
    Ok(())
}

fn commit_savepoint(conn: &Connection, name: &str) -> Result<()> {
    let stmt = format!("RELEASE {}", name);
    conn.execute(&stmt, [])?;
    Ok(())
}

pub fn newest_osm_object_timestamp(conn: &Connection) -> Result<String> {
    let mut stmt = conn.prepare_cached("SELECT max(newest_osm_object_timestamp) from areas")?;
    Ok(stmt.query_row([], |r| Ok(r.get_unwrap(0)))?)
}

pub fn areas_containing(entity_id: &str, conn: &Connection) -> Result<Vec<i64>> {
    let mut stmt = conn.prepare_cached("SELECT area_id from area_entities WHERE entity_id = ?")?;
    let ids = stmt
        .query_map([entity_id], |r| Ok(r.get_unwrap(0)))?
        .map(|a| a.expect("Could not get area id"))
        .collect();
    Ok(ids)
}

pub fn entities_containing(child_id: &str, conn: &Connection) -> Result<Vec<String>> {
    let mut stmt = conn.prepare_cached(
        "SELECT entity_id from entity_geometry_parts WHERE contained_entity_id = ?",
    )?;
    let ids = stmt
        .query_map([child_id], |r| Ok(r.get_unwrap(0)))?
        .map(|a| a.expect("Could not get area id"))
        .collect();
    Ok(ids)
}

pub(crate) fn delete_entity_records(conn: &Connection, entity_id: &str) -> Result<()> {
    delete_entity_geometry_parts(conn, entity_id)?;
    let mut del_entity_stmt =
        conn.prepare_cached("DELETE FROM area_entities WHERE entity_id = ?")?;
    del_entity_stmt.execute([entity_id])?;
    Ok(())
}

pub(crate) fn delete_entity_geometry_parts(conn: &Connection, entity_id: &str) -> Result<()> {
    let mut del_geometry_parts_stmt =
        conn.prepare_cached("DELETE FROM entity_geometry_parts WHERE entity_id = ?")?;
    del_geometry_parts_stmt.execute([entity_id])?;
    Ok(())
}

pub(crate) fn delete_area_entity(conn: &Connection, area_id: i64, entity_id: &str) -> Result<()> {
    let mut del_entity_stmt =
        conn.prepare_cached("DELETE FROM area_entities WHERE area_id = ? AND entity_id = ?")?;
    del_entity_stmt.execute((area_id, entity_id))?;
    Ok(())
}

pub fn insert_or_update_changeset(
    conn: &Connection,
    changeset: &InsertableChangeset,
    changesets_batch: u32,
) -> Result<()> {
    let mut stmt = conn.prepare_cached("INSERT OR REPLACE INTO changesets (changeset_id, changesets_batch, min_lat, max_lat, min_lon, max_lon) VALUES (?, ?, ?, ?, ?, ?)")?;
    stmt.execute((
        changeset.id,
        changesets_batch,
        changeset.min_lat,
        changeset.max_lat,
        changeset.min_lon,
        changeset.max_lon,
    ))?;
    Ok(())
}

pub(crate) fn get_changeset(conn: &Connection, changeset_id: u64) -> Result<Option<Changeset>> {
    let mut stmt = conn.prepare_cached("SELECT changeset_id, changesets_batch, min_lat, max_lat, min_lon, max_lon FROM changesets WHERE changeset_id = ?")?;
    let mut rows = stmt.query([changeset_id])?;
    if let Some(row) = rows.next()? {
        Ok(Some(Changeset {
            id: row.get_unwrap(0),
            batch: row.get_unwrap(1),
            bounds: BoundaryRect {
                min_x: row.get_unwrap(4),
                min_y: row.get_unwrap(2),
                max_x: row.get_unwrap(5),
                max_y: row.get_unwrap(3),
            },
        }))
    } else {
        Ok(None)
    }
}
