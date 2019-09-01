use crate::{amqp_utils, Result};
use lapin::options::{
    BasicPublishOptions, ExchangeDeclareOptions, QueueBindOptions, QueueDeclareOptions,
};
use lapin::types::FieldTable;
use lapin::{BasicProperties, Channel};
use osm_db::semantic_change::SemanticChange;
use serde_json;
use sha3::{Digest, Sha3_256};

fn queue_name_for(client_id: &str, area_name: &str) -> String {
    let to_hash = format!("{}{}", client_id, area_name);
    let hash = Sha3_256::digest(&to_hash.into_bytes());
    hex::encode(hash)
}

pub fn init_queue(client_id: &str, area_name: &str) -> Result<()> {
    let client = amqp_utils::connect_to_broker()?;
    let channel = client.create_channel().wait()?;
    let opts = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };
    let queue_name = queue_name_for(&client_id, &area_name);
    channel
        .queue_declare(&queue_name, opts, FieldTable::default())
        .wait()?;
    channel
        .queue_bind(
            &queue_name,
            &area_name,
            "",
            QueueBindOptions::default(),
            FieldTable::default(),
        )
        .wait()?;
    channel.close(0, "Normal shutdown").wait()?;
    Ok(())
}

pub fn publish_change_on(
    channel: &Channel,
    change: &SemanticChange,
    area_name: &str,
) -> Result<()> {
    let serialized = serde_json::to_string(&change)?;
    let props = BasicProperties::default().with_delivery_mode(2);
    channel
        .basic_publish(
            &area_name,
            "",
            BasicPublishOptions::default(),
            serialized.into_bytes(),
            props,
        )
        .wait()?;
    Ok(())
}

pub fn publish_change(change: &SemanticChange, area_name: &str) -> Result<()> {
    let amqp_conn = amqp_utils::connect_to_broker()?;
    let channel = amqp_conn.create_channel().wait()?;
    publish_change_on(&channel, change, area_name)?;
    channel.close(0, "Normal shutdown").wait()?;
    Ok(())
}

pub fn init_exchange(area_name: &str) -> Result<()> {
    let client = amqp_utils::connect_to_broker()?;
    let channel = client.create_channel().wait()?;
    let opts = ExchangeDeclareOptions {
        durable: true,
        ..Default::default()
    };
    channel
        .exchange_declare(&area_name, "fanout", opts, FieldTable::default())
        .wait()?;
    Ok(())
}