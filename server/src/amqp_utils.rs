use crate::background_task_constants;
use crate::Result;
use lapin_futures::{Channel, Client, ConnectionProperties};
use lapin_futures::options::QueueDeclareOptions;
use lapin_futures::auth::Credentials;
use lapin_async::Queue;
use lapin_futures::types::{AMQPValue, FieldTable};
use lapin_futures::uri::AMQPUri;
use std::env;
use std::str::FromStr;
use tokio::await;

pub async fn connect_to_broker() -> Result<Client> {
    let uri = AMQPUri::from_str(&env::var("AMQP_BROKER_URL")?).map_err(|e| failure::err_msg(e))?;
    let credentials = Credentials::new(uri.authority.userinfo.username.clone(), uri.authority.userinfo.password.clone());
    let client = await!(Client::connect_uri(
        uri, credentials, ConnectionProperties::default()
    ))?;
    info!("Broker connection established.");
    Ok(client)
}

pub async fn init_background_job_queues(channel: &mut Channel) -> Result<(Queue, Queue)>
{
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
