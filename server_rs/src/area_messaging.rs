use crate::{amqp_utils, Result};
use lapin_futures::channel::{QueueBindOptions, QueueDeclareOptions};
use lapin_futures::types::FieldTable;
use sha3::{Digest, Sha3_256};
use tokio::await;

fn queue_name_for(client_id: &str, area_name: &str) -> String {
    let to_hash = format!("{}{}", client_id, area_name);
    let hash = Sha3_256::digest(&to_hash.into_bytes());
    hex::encode(hash)
}

async fn init_queue_real(client_id: String, area_name: String) -> Result<()> {
    let client = await!(amqp_utils::connect_to_broker())?;
    let channel = await!(client.create_channel())?;
    let opts = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };
    let queue_name = queue_name_for(&client_id, &area_name);
    await!(channel.queue_declare(&queue_name, opts, FieldTable::new()))?;
    await!(channel.queue_bind(
        &queue_name,
        &area_name,
        "",
        QueueBindOptions::default(),
        FieldTable::new()
    ))?;
    Ok(())
}

pub async fn init_queue(client_id: String, area_name: String) {
    if let Err(e) = await!(init_queue_real(client_id, area_name)) {
        error!("Error during queue creation and exchange binding: {}", e);
    }
}
