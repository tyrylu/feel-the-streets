use anyhow::Result;
use crate::rabbitmq_admin_api::Client;
use diesel::{Connection, SqliteConnection};
use lapin::options::QueuePurgeOptions;
use osm_db::semantic_change::SemanticChange;
use server::amqp_utils;
use server::area::Area;
use server::area_messaging;
use std::env;

pub fn request_redownload(all: bool, area: Option<i64>) -> Result<()> {
    let _dotenv_path = dotenv::dotenv()?;
    let management_uri = env::var("RABBITMQ_MANAGEMENT_URI")?;
    let client = Client::new(management_uri)?;
    let areas = if all {
        let server_conn = SqliteConnection::establish("server.db")?;
Area::all(&server_conn)?.iter().map(|a| a.osm_id).collect()
    }
    else {
        vec![area.unwrap()]
    };
    let amqp_client = amqp_utils::connect_to_broker()?;
    let channel = amqp_client.create_channel().wait()?;
for area_id in areas {
    println!("Processing area {}", area_id);
    for binding in client.get_queues_bound_to_exchange("%2f", &area_id.to_string())? {
        println!("Purging bound queue {}", binding.destination);
        let message_count = channel.queue_purge(&binding.destination, QueuePurgeOptions::default()).wait()?;
        println!("Purged {} messages from the queue, sending redownload message.", message_count);
            }
            println!("Publishing the redownload request...");
            area_messaging::publish_change_on(&channel, &SemanticChange::RedownloadDatabase, area_id)?;
            println!("Success.");
}
    Ok(())
}