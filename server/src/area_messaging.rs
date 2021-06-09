use crate::{amqp_utils, Result};
use lapin::options::{
    BasicPublishOptions, ExchangeDeclareOptions, QueueBindOptions, QueueDeclareOptions,
    QueuePurgeOptions,
};
use lapin::types::FieldTable;
use lapin::{BasicProperties, Channel, ExchangeKind};
use osm_db::semantic_change::SemanticChange;
use sha3::{Digest, Sha3_256};

fn queue_name_for(client_id: &str, area_osm_id: i64) -> String {
    let to_hash = format!("{}{}", client_id, area_osm_id);
    let hash = Sha3_256::digest(&to_hash.into_bytes());
    hex::encode(hash)
}

pub fn init_queue(client_id: &str, area_osm_id: i64) -> Result<()> {
    let client = amqp_utils::connect_to_broker()?;
    let channel = client.create_channel().wait()?;
    let opts = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };
    let queue_name = queue_name_for(client_id, area_osm_id);
    channel
        .queue_declare(&queue_name, opts, FieldTable::default())
        .wait()?;
    channel
        .queue_purge(&queue_name, QueuePurgeOptions::default())
        .wait()?;
    channel
        .queue_bind(
            &queue_name,
            &area_osm_id.to_string(),
            "",
            QueueBindOptions::default(),
            FieldTable::default(),
        )
        .wait()?;
    Ok(())
}

pub fn publish_change_on(
    channel: &Channel,
    change: &SemanticChange,
    area_osm_id: i64,
) -> Result<()> {
    let compressed = change.serialize()?;
    let props = BasicProperties::default().with_delivery_mode(2);
    channel
        .basic_publish(
            &area_osm_id.to_string(),
            "",
            BasicPublishOptions::default(),
            compressed,
            props,
        )
        .wait()?;
    Ok(())
}

pub fn publish_change(change: &SemanticChange, area_osm_id: i64) -> Result<()> {
    let amqp_conn = amqp_utils::connect_to_broker()?;
    let channel = amqp_conn.create_channel().wait()?;
    publish_change_on(&channel, change, area_osm_id)?;
    Ok(())
}

pub fn init_exchange(area_osm_id: i64) -> Result<()> {
    let client = amqp_utils::connect_to_broker()?;
    let channel = client.create_channel().wait()?;
    let opts = ExchangeDeclareOptions {
        durable: true,
        ..Default::default()
    };
    channel
        .exchange_declare(
            &area_osm_id.to_string(),
            ExchangeKind::Fanout,
            opts,
            FieldTable::default(),
        )
        .wait()?;
    Ok(())
}
