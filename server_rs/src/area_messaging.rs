use crate::{amqp_utils, Result};
use lapin_futures::channel::{
    BasicProperties, BasicPublishOptions, QueueBindOptions, QueueDeclareOptions,
};
use lapin_futures::types::FieldTable;
use log::error;
use osm_db::semantic_change::SemanticChange;
use serde_json;
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

async fn publish_change_internal(change: SemanticChange, area_name: String) -> Result<()> {
    let serialized = serde_json::to_string(&change)?;
    let props = BasicProperties::default().with_delivery_mode(2);
    let amqp_conn = await!(amqp_utils::connect_to_broker())?;
    let channel = await!(amqp_conn.create_channel())?;
    await!(channel.basic_publish(
        &area_name,
        "",
        serialized.into_bytes(),
        BasicPublishOptions::default(),
        props
    ))?;
    Ok(())
}
pub async fn publish_change(change: SemanticChange, area_name: String) {
    if let Err(e) = await!(publish_change_internal(change, area_name)) {
        error!("Error during change publishing: {}", e);
    }
}
