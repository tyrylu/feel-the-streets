use crate::background_task_constants;
use crate::Result;
use futures::future::Future;
use lapin_futures::channel::{Channel, QueueDeclareOptions};
use lapin_futures::client::{Client, ConnectionOptions, ConnectionProperties, HeartbeatHandle};
use lapin_futures::queue::Queue;
use lapin_futures::types::{AMQPValue, FieldTable};
use lapin_futures::uri::AMQPUri;
use std::env;
use std::net::SocketAddr;
use std::str::FromStr;
use tokio::await;
use tokio::io::{AsyncRead, AsyncWrite};
use tokio::net::TcpStream;

pub async fn connect_to_broker() -> Result<(Client<TcpStream>, HeartbeatHandle)> {
    let uri = AMQPUri::from_str(&env::var("AMQP_BROKER_URL")?).map_err(|e| failure::err_msg(e))?;
    let host_addr: SocketAddr = format!("{}:{}", uri.authority.host, uri.authority.port).parse()?;
    let stream = await!(TcpStream::connect(&host_addr))?;
    info!("TCP connection to host {} established.", &host_addr);
    let (client, mut heartbeat) = await!(Client::connect(
        stream,
        ConnectionOptions::from_uri(uri, ConnectionProperties::default())
    ))?;
    info!("Broker connection established.");
    // A newly spawned future can not return an error, so logging it is the best we can hope for.
    let handle = heartbeat.handle().unwrap();
    tokio::spawn(heartbeat.map_err(|e| error!("Error in heardbeat: {}", e)));
    Ok((client, handle))
}

pub async fn init_background_job_queues<T>(channel: &mut Channel<T>) -> Result<(Queue, Queue)>
where
    T: AsyncRead + AsyncWrite + Send + Sync + 'static,
{
    let opts = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };
    let tasks_queue = await!(channel.queue_declare(
        background_task_constants::TASKS_QUEUE,
        opts,
        FieldTable::new()
    ))?;
    let mut args = FieldTable::new();
    args.insert(
        "x-dead-letter-exchange".to_string(),
        AMQPValue::LongString("".to_string()),
    );
    args.insert(
        "x-dead-letter-routing-key".to_string(),
        AMQPValue::LongString(background_task_constants::TASKS_QUEUE.to_string()),
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
