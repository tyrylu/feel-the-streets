use anyhow::Result;
use diesel::{Connection, SqliteConnection};
use lapin::options::ConfirmSelectOptions;
use osm_db::area_db::AreaDatabase;
use osm_db::entities_query::EntitiesQuery;
use osm_db::entities_query_condition::{Condition, FieldCondition};
use osm_db::semantic_change::{EntryChange, SemanticChange};
use server::amqp_utils;
use server::area::Area;
use server::area_messaging;

pub fn remove_field(entity: String, field: String, new_name: Option<String>) -> Result<()> {
    let _dotenv_path = dotenv::dotenv()?;
    let server_conn = SqliteConnection::establish("server.db")?;
    let amq_conn = amqp_utils::connect_to_broker().expect("Amqp connect fail");
    let channel = amq_conn.create_channel().wait().expect("Create channel fail");
    channel
        .confirm_select(ConfirmSelectOptions::default())
        .wait().expect("Confirm select fail");
    for area in Area::all_updated(&server_conn)? {
        println!("Processing area {} (id {})...", area.name, area.osm_id);
        let area_db = AreaDatabase::open_existing(area.osm_id, true)?;
        let mut query = EntitiesQuery::default();
        query.set_included_discriminators(vec![entity.clone()]);
        query.add_condition(FieldCondition::new(field.clone(), Condition::IsNotNull));
        let mut changes = vec![];
        for mut entity in area_db.get_entities(&query)?.into_iter() {
            let val = entity.value_of_field(&field).clone();
            let mut entry_changes = vec![EntryChange::removing(&field)];
            if let Some(new_name) = &new_name {
                entry_changes.push(EntryChange::creating(&new_name, val));
            }
            changes.push(SemanticChange::updating(
                entity
                    .value_of_field("osm_id")
                    .as_str()
                    .expect("OSM Id not a string?"),
                vec![],
                entry_changes,
                vec![],
            ));
        }
        if new_name.is_some() {
            println!(
                "Applying and publishing {} changes resulting from the rename...",
                changes.len()
            );
        } else {
            println!(
                "Applying and publishing {} changes resulting from the removal...",
                changes.len()
            );
        }
        area_db.begin()?;
        for change in &changes {
            area_db.apply_change(change)?;
            area_messaging::publish_change_on(&channel, change, area.osm_id).expect("Publish change fail");
            for confirmation in channel.wait_for_confirms().wait().expect("Wait for confirms fail") {
                if confirmation.reply_code != 200 {
                    eprintln!(
                        "Non 200 reply code from delivery: {:?}, code: {}, message: {}",
                        confirmation.delivery, confirmation.reply_code, confirmation.reply_text
                    );
                }
            }
        }
        area_db.commit()?;
        println!("Area processed successfully.");
    }
    println!("Cleaning up...");
    Ok(())
}
