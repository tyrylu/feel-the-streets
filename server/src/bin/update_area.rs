use diesel::{Connection, SqliteConnection};
use osm_db::translation::record::TranslationRecord;
use server::{area::Area, Result};

fn main() -> Result<()> {
    let _dotenv_path = dotenv::dotenv()?;
    server::init_logging();
    let area_db_conn = SqliteConnection::establish("server.db")?;
    let mut record = TranslationRecord::new();
    let area_id: i64 = std::env::args()
        .nth(1)
        .expect("Area id not provided")
        .parse()
        .expect("Area id not an int");
    let mut area = Area::find_by_osm_id(area_id, &area_db_conn)?;
    server::background_tasks::area_db_update::update_area(&mut area, &area_db_conn, &mut record)?;
    Ok(())
}
