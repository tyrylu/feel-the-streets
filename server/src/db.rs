pub use rusqlite::Connection;
use crate::Result;

pub fn connect_to_server_db() -> Result<Connection> {
    let conn = Connection::open("server.db")?;
    unsafe {
        conn.load_extension_enable()?;
        conn.load_extension("mod_spatialite", None)?;
    }
    conn.load_extension_disable()?;
    Ok(conn)
}