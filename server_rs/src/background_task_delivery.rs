use crate::{amqp_utils, background_task::BackgroundTask, background_task_constants, Result};
use lapin_futures::channel::{BasicProperties, BasicPublishOptions};
use tokio::await;

async fn deliver_real(task: &BackgroundTask, ttl: Option<u32>) -> Result<()> {
    let client = await!(amqp_utils::connect_to_broker())?;
    await!(amqp_utils::init_background_job_queues(&client))?;
    let channel = await!(client.create_channel())?;
    let msg = serde_json::to_string(&task)?;
    let mut props = BasicProperties::default().with_delivery_mode(2);
    let queue_name = if let Some(ttl) = ttl {
        props = props.with_expiration(ttl.to_string());
    background_task_constants::FUTURE_TASKS_QUEUE
    }
    else {
        background_task_constants::TASKS_QUEUE
    };
    await!(channel.basic_publish(
        "",
        queue_name,
        msg.into_bytes(),
        BasicPublishOptions::default(),
        props
    ))?;
    Ok(())
}

pub async fn deliver(task: BackgroundTask, ttl: Option<u32>) {
    let res = await!(deliver_real(&task, ttl));
    if let Err(e) = res {
        error!("Error during message delivery: {}", e);
    }
}
