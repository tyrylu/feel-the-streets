use diesel::{Connection, SqliteConnection};
use lapin::options::ConfirmSelectOptions;
use osm_db::translation::record::TranslationRecord;
use server::{area::Area, amqp_utils, Result};

fn main() -> Result<()> {
    server::init_logging();
    let area_db_conn = SqliteConnection::establish("server.db")?;
    let mut record = TranslationRecord::new();
    let area_id: i64 = std::env::args().nth(1).expect("Area id not provided").parse().expect("Area id not an int");
    let mut area = Area::find_by_osm_id(area_id, &area_db_conn)?;
    let rabbitmq_conn = amqp_utils::connect_to_broker()?;
    let channel = rabbitmq_conn.create_channel().wait()?;
    channel
        .confirm_select(ConfirmSelectOptions::default())
        .wait()?;
    server::background_tasks::area_db_update::update_area(&mut area, &area_db_conn, &channel, &mut record)?;
    Ok(())
}