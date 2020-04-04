use crate::background_task_constants;
use crate::Result;
use lapin::options::QueueDeclareOptions;
use lapin::types::{AMQPValue, FieldTable};
use lapin::Queue;
use lapin::{Channel, Connection, ConnectionProperties, CloseOnDrop};
use std::env;

pub fn connect_to_broker() -> Result<CloseOnDrop<Connection>> {
    let client = Connection::connect(
        &env::var("AMQP_BROKER_URL")?,
        ConnectionProperties::default(),
    )
    .wait()?;
    info!("Broker connection established.");
    Ok(client)
}

pub fn init_background_job_queues(channel: &Channel) -> Result<(Queue, Queue)> {
    let opts = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };
    let tasks_queue = channel
        .queue_declare(
            background_task_constants::TASKS_QUEUE,
            opts,
            FieldTable::default(),
        )
        .wait()?;
    let mut args = FieldTable::default();
    args.insert(
        "x-dead-letter-exchange".into(),
        AMQPValue::LongString("".into()),
    );
    args.insert(
        "x-dead-letter-routing-key".into(),
        AMQPValue::LongString(background_task_constants::TASKS_QUEUE.into()),
    );
    let opts2 = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };
    let future_tasks_queue = channel
        .queue_declare(background_task_constants::FUTURE_TASKS_QUEUE, opts2, args)
        .wait()?;
    info!("Queues initialized.");
    Ok((tasks_queue, future_tasks_queue))
}
