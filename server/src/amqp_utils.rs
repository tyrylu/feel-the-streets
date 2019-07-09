use crate::background_task_constants;
use crate::Result;
use lapin::Queue;
use lapin_futures::options::QueueDeclareOptions;
use lapin_futures::types::{AMQPValue, FieldTable};
use lapin_futures::{Channel, Client, ConnectionProperties};
use std::env;
use tokio::await;

pub async fn connect_to_broker() -> Result<Client> {
    let client = await!(Client::connect(
        &env::var("AMQP_BROKER_URL")?,
        ConnectionProperties::default()
    ))?;
    info!("Broker connection established.");
    Ok(client)
}

pub async fn init_background_job_queues(channel: &mut Channel) -> Result<(Queue, Queue)> {
    let opts = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };
    let tasks_queue = await!(channel.queue_declare(
        background_task_constants::TASKS_QUEUE,
        opts,
        FieldTable::default()
    ))?;
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
    let future_tasks_queue =
        await!(channel.queue_declare(background_task_constants::FUTURE_TASKS_QUEUE, opts2, args))?;
    info!("Queues initialized.");
    Ok((tasks_queue, future_tasks_queue))
}
