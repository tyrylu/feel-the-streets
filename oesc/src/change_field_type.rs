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

pub fn change_field_type(entity: String, field: String, new_type: String) -> Result<()> {
    let _dotenv_path = dotenv::dotenv()?;
    let server_conn = SqliteConnection::establish("server.db")?;
    let amq_conn = amqp_utils::connect_to_broker()?;
    let channel = amq_conn.create_channel().wait()?;
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
    println!("Could not interpret value {} as the requested type {}, change will not be executed.", old_val, new_type);
    process::exit(1);
}
        }
println!("Applying and publishing {} changes resulting from the type change...", changes.len());
for change in &changes {
    area_db.apply_change(change)?;
    area_messaging::publish_change_on(&channel, change, area.osm_id)?;
}
println!("Area processed successfully.");
    }
println!("Cleaning up...");
channel.close(0, "Normal shutdown").wait()?;
amq_conn.close(0, "Normal shutdown").wait()?;
    Ok(())
}