use anyhow::Result;
use osm_db::area_db::AreaDatabase;
use osm_db::entities_query::EntitiesQuery;
use osm_db::entities_query_condition::{Condition, FieldCondition};
use osm_db::semantic_change::{EntryChange, SemanticChange};
use osm_db::translation::{conversions, record::TranslationRecord};
use redis_api::ChangesStream;
use server::area::Area;
use server::db;
use std::process;

pub fn change_field_type(
    entity: String,
    field: String,
    new_type: String,
    force: bool,
) -> Result<()> {
    let server_conn = db::connect_to_server_db()?;
    for area in Area::all_updated(&server_conn)? {
        println!("Processing area {} (id {})...", area.name, area.osm_id);
        let mut area_db = AreaDatabase::open_existing(area.osm_id, true)?;
        let mut query = EntitiesQuery::default();
        query.set_included_discriminators(vec![entity.clone()]);
        query.add_condition(FieldCondition::new(field.clone(), Condition::IsNotNull));
        let mut changes = vec![];
        let mut record = TranslationRecord::new();
        for mut entity in area_db.get_entities(&query)?.into_iter() {
            let old_val = entity.value_of_field(&field).clone();
            let old_val_str = match old_val.as_str() {
                Some(s) => s,
                None => {
                    if force {
                        eprintln!(
                            "Value {old_val} was not a string, continuing because of the force flag."
                        );
                        continue;
                    } else {
                        eprintln!("Value {old_val} was not a string.");
                        process::exit(1);
                    }
                }
            };

            if let Some(new_val) =
                conversions::convert_field_value(old_val_str, &new_type, &mut record)
            {
                changes.push(SemanticChange::updating(
                    entity
                        .value_of_field("osm_id")
                        .as_str()
                        .expect("OSM Id not a string?"),
                    vec![],
                    vec![EntryChange::updating(&field, old_val, new_val)],
                    vec![],
                ));
            } else if !force {
                eprintln!("Could not interpret value {old_val} as the requested type {new_type}, change will not be executed.");
                process::exit(1);
            } else {
                eprintln!("Could not interpret value {old_val} as the requested type {new_type}, continuing regardless, force flag is in effect.");
            }
        }
        println!(
            "Applying and publishing {} changes resulting from the type change...",
            changes.len()
        );
        area_db.begin()?;
        let mut stream = ChangesStream::new_from_env(area.osm_id)?;
        let mut batch = stream.begin_batch();
        for change in &changes {
            area_db.apply_change(change)?;
            batch.add_change(change)?;
        }
        area_db.commit()?;
        println!("Area processed successfully.");
    }
    println!("Cleaning up...");
    Ok(())
}
