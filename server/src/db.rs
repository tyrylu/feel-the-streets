use osm_api::BoundaryRect;
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
    Ok(conn)
}

pub fn get_geometry_bounds(conn: &Connection, geometry: &[u8]) -> Result<BoundaryRect> {
    let mut stmt = conn.prepare_cached("SELECT MbrMinX(GeomFromWkb(:geom, 4326)) as minx, MbrMinY(GeomFromWkb(:geom, 4326)) as miny, MbrMaxX(GeomFromWkb(:geom, 4326)) as maxx, MbrMaxY(GeomFromWkb(:geom, 4326)) as maxy")?;
    Ok(stmt.query_row(named_params! {":geom": geometry}, |r| Ok(BoundaryRect {
        min_x: r.get_unwrap(0),
        min_y: r.get_unwrap(1),
        max_x: r.get_unwrap(2),
        max_y: r.get_unwrap(3)
    }))?)
}