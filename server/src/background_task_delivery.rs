use crate::{amqp_utils, background_task::BackgroundTask, background_task_constants, Result};
use lapin::options::BasicPublishOptions;
use lapin::{BasicProperties, Channel};

pub fn perform_delivery_on(
    channel: &Channel,
    task: &BackgroundTask,
    ttl: Option<u32>,
) -> Result<()> {
    let msg = serde_json::to_string(&task)?;
    let mut props = BasicProperties::default().with_delivery_mode(2);
    let queue_name = if let Some(ttl) = ttl {
        props = props.with_expiration(ttl.to_string().as_str().into());
        background_task_constants::FUTURE_TASKS_QUEUE
    } else {
        background_task_constants::TASKS_QUEUE
    };
    channel
        .basic_publish(
            "",
            queue_name,
            BasicPublishOptions::default(),
            msg.into_bytes(),
            props,
        )
        .wait()?;
    info!("Task delivered.");
    Ok(())
}

pub fn deliver(task: &BackgroundTask, ttl: Option<u32>) -> Result<()> {
    let client = amqp_utils::connect_to_broker()?;
    let channel = client.create_channel().wait()?;
    amqp_utils::init_background_job_queues(&channel)?;
    perform_delivery_on(&channel, task, ttl)?;
    Ok(())
}
