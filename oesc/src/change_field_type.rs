use lapin::options::ConfirmSelectOptions;
use anyhow::Result;
use osm_db::area_db::AreaDatabase;
use osm_db::entities_query::EntitiesQuery;
use osm_db::entities_query_condition::{Condition, FieldCondition};
use osm_db::translation::conversions;
use osm_db::semantic_change::{SemanticChange, EntryChange};
use diesel::{Connection, SqliteConnection};
use server::area::Area;
use server::amqp_utils;
use server::area_messaging;
use std::process;

pub fn change_field_type(entity: String, field: String, new_type: String, force: bool) -> Result<()> {
    let _dotenv_path = dotenv::dotenv()?;
    let server_conn = SqliteConnection::establish("server.db")?;
    let amq_conn = amqp_utils::connect_to_broker()?;
    let channel = amq_conn.create_channel().wait()?;
    channel.confirm_select(ConfirmSelectOptions::default()).wait()?;
    for area in Area::all_updated(&server_conn)? {
        println!("Processing area {} (id {})...", area.name, area.osm_id);
        let area_db = AreaDatabase::open_existing(area.osm_id, true)?;
        let mut query = EntitiesQuery::default();
        query.set_included_discriminators(vec![entity.clone()]);
        query.add_condition(FieldCondition::new(field.clone(), Condition::IsNotNull));
        let mut changes = vec![];
        for mut entity in area_db.get_entities(&query)?.into_iter() {
let old_val = entity.value_of_field(&field).clone();
let old_val_str = old_val.as_str().expect("Before conversion, the field was not a mere string.");
if let Some(new_val) = conversions::convert_field_value(&old_val_str, &new_type) {
changes.push(SemanticChange::updating(entity.value_of_field("osm_id").as_str().expect("OSM Id not a string?"), vec![], vec![EntryChange::updating(&field, old_val, new_val)]));
}
else {
    if force {
    eprintln!("Could not interpret value {} as the requested type {}, change will not be executed.", old_val, new_type);
    process::exit(1);
    }
    else {
        eprintln!("Could not interpret value {} as the requested type {}, continuing regardless, force flag is in effect.", old_val, new_type);
    }
}
        }
println!("Applying and publishing {} changes resulting from the type change...", changes.len());
area_db.begin()?;
for change in &changes {
    area_db.apply_change(change)?;
    area_messaging::publish_change_on(&channel, change, area.osm_id)?;
    for confirmation in channel.wait_for_confirms().wait()? {
        if confirmation.reply_code != 200 {
            eprintln!("Non 200 reply code from delivery: {:?}, code: {}, message: {}", confirmation.delivery, confirmation.reply_code, confirmation.reply_text);
        }
    }
}
area_db.commit()?;
println!("Area processed successfully.");
    }
println!("Cleaning up...");
channel.close(200, "Normal shutdown").wait()?;
amq_conn.close(200, "Normal shutdown").wait()?;
    Ok(())
}