use crate::background_task_constants;
use crate::Result;
use futures::future::Future;
use lapin_futures::channel::QueueDeclareOptions;
use lapin_futures::client::{Client, ConnectionOptions, ConnectionProperties};
use lapin_futures::types::{AMQPValue, FieldTable};
use lapin_futures::uri::AMQPUri;
use std::env;
use std::net::SocketAddr;
use std::str::FromStr;
use tokio::await;
use tokio::io::{AsyncRead, AsyncWrite};
use tokio::net::TcpStream;

pub async fn connect_to_broker() -> Result<Client<TcpStream>> {
    let uri = AMQPUri::from_str(&env::var("AMQP_BROKER_URL")?).map_err(|e| failure::err_msg(e))?;
    let host_addr: SocketAddr = format!("{}:{}", uri.authority.host, uri.authority.port).parse()?;
    let stream = await!(TcpStream::connect(&host_addr))?;
    info!("TCP connection to host {} established.", &host_addr);
    let (client, heardbeat) = await!(Client::connect(stream, ConnectionOptions::from_uri(uri, ConnectionProperties::default())))?;
    info!("Broker connection established.");
    // A newly spawned future can not return an error, so logging it is the best we can hope for.
    tokio::spawn(heardbeat.map_err(|e| error!("Error in heardbeat: {}", e)));
    Ok(client)
}

pub async fn init_background_job_queues<T>(client: &Client<T>) -> Result<()>
where
    T: AsyncRead + AsyncWrite + Send + Sync + 'static,
{
    let channel = await!(client.create_channel())?;
    let opts = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };
    await!(channel.queue_declare(
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
    await!(channel.queue_declare(background_task_constants::FUTURE_TASKS_QUEUE, opts2, args))?;
    await!(channel.close(0, "Normal shutdown"))?;
    info!("Queues initialized.");
    Ok(())
}
