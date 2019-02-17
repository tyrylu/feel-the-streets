use crate::{amqp_utils, background_task::BackgroundTask, background_task_constants, Result};
use lapin_futures::channel::{BasicProperties, BasicPublishOptions};
use tokio::await;

async fn deliver_real(task: &BackgroundTask) -> Result<()> {
    let client = await!(amqp_utils::connect_to_broker())?;
    await!(amqp_utils::init_background_job_queues(&client))?;
    let channel = await!(client.create_channel())?;
    let msg = serde_json::to_string(&task)?;
    let props = BasicProperties::default().with_delivery_mode(1);
    await!(channel.basic_publish(
        "",
        background_task_constants::TASKS_QUEUE,
        msg.into_bytes(),
        BasicPublishOptions::default(),
        props
    ))?;
    Ok(())
}

pub async fn deliver(task: BackgroundTask) {
    let res = await!(deliver_real(&task));
    if let Err(e) = res {
        error!("Error during message delivery: {}", e);
    }
}
